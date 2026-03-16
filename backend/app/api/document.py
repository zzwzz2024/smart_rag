"""
文档管理 API
"""
import os
import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.database import get_db, async_session_factory
from backend.app.models.user import User
from backend.app.models.document import Document, DocumentChunk, DocumentRole
from backend.app.models.knowledge_base import KnowledgeBase
from backend.app.models.model import Model
from backend.app.models.system import Role
from backend.app.schemas.document import DocumentResponse, ChunkResponse, DocumentPermissionResponse
from backend.app.utils.auth import get_current_user
from backend.app.services.doc_service import process_document
from backend.app.core.vector_store import VectorStore
from backend.app.config import get_settings
import backend.app.services.chat_service as chat_service
from backend.app.core.rag_pipeline import RAGPipeline
from backend.app.models.response_model import Response
from loguru import logger
# 获取文档的角色权限
from backend.app.schemas.document import DocumentPermissionResponse
from sqlalchemy import or_, and_, func, exists
from datetime import datetime
from sqlalchemy import update

router = APIRouter()
settings = get_settings()
vector_store = VectorStore()


@router.post("/initialize/{kb_id}", response_model=Response)
async def initialize_kb_models(
    kb_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """初始化知识库关联的模型"""
    # 验证知识库
    result = await db.execute(
        select(KnowledgeBase).where(KnowledgeBase.id == kb_id, KnowledgeBase.is_deleted == False)
    )
    kb = result.scalar_one_or_none()
    if not kb or kb.owner_id != user.id:
        raise HTTPException(404, "知识库不存在")

    # 初始化模型变量
    embedding_model = None
    rerank_model = None
    api_key = None
    base_url = None

    # 获取embedding模型详情
    if kb.embedding_model_id:
        embedding_model_result = await db.execute(
            select(Model).where(Model.id == kb.embedding_model_id, Model.is_active == True)
        )
        embedding_model = embedding_model_result.scalar_one_or_none()
        if embedding_model:
            api_key = embedding_model.api_key
            base_url = embedding_model.base_url

    # 获取rerank模型详情
    if kb.rerank_model_id:
        rerank_model_result = await db.execute(
            select(Model).where(Model.id == kb.rerank_model_id, Model.is_active == True)
        )
        rerank_model = rerank_model_result.scalar_one_or_none()

    # 初始化RAG pipeline，传递知识库关联的模型
    chat_service.rag_pipeline = RAGPipeline(
        api_key=api_key,
        base_url=base_url,
        embedding_model=embedding_model,
        rerank_model=rerank_model
    )

    return Response(data={
        "message": f"知识库 {kb.name} 模型初始化成功",
        "kb_id": kb_id,
        "embedding_model": embedding_model.name if embedding_model else "None",
        "rerank_model": rerank_model.name if rerank_model else "None"
    })


@router.post("/upload/{kb_id}", response_model=Response)
async def upload_document(
    kb_id: str,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """上传文档到知识库"""
    # 验证知识库
    result = await db.execute(
        select(KnowledgeBase).where(KnowledgeBase.id == kb_id, KnowledgeBase.is_deleted == False)
    )
    kb = result.scalar_one_or_none()
    if not kb or kb.owner_id != user.id:
        raise HTTPException(404, "知识库不存在")

    # 验证文件类型
    ext = os.path.splitext(file.filename)[1].lower()
    allowed = {".pdf", ".docx", ".txt", ".md", ".pptx", ".xlsx", ".csv", ".html"}
    if ext not in allowed:
        raise HTTPException(400, f"不支持的文件类型: {ext}")

    # 保存文件
    upload_dir = os.path.join(settings.UPLOAD_DIR, kb_id)
    os.makedirs(upload_dir, exist_ok=True)

    file_id = str(uuid.uuid4())
    file_path = os.path.join(upload_dir, f"{file_id}{ext}")

    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    # 直接处理文档，处理成功后才返回响应
    try:
        # 1. 创建文档记录（状态为processing）
        doc = Document(
            id=file_id,
            kb_id=kb_id,
            filename=file.filename,
            file_path=file_path,
            file_type=ext.lstrip("."),
            file_size=len(content),
            status="processing",
        )
        db.add(doc)
        
        # 2. 处理文档（包括分块、向量化等）
        await process_document(db, file_id)
        
        # 3. 提交事务，只有处理成功才会保存到数据库
        await db.commit()
        
        return Response(data={
            "message": "文档上传成功",
            "file_id": file_id,
            "filename": file.filename
        })
    except Exception as e:
        # 如果处理失败，回滚事务
        await db.rollback()
        # 清理上传的文件
        if os.path.exists(file_path):
            os.remove(file_path)
        logger.error(f"文档上传失败: {e}")
        raise HTTPException(500, f"文档上传失败: {str(e)}")




@router.get("/list/{kb_id}", response_model=Response)
async def list_documents(
    kb_id: str,
    filename: str = None,
    created_from: str = None,
    created_to: str = None,
    page: int = 1,
    page_size: int = 10,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """获取知识库下的文档列表"""

    # 构建查询
    base_stmt = select(Document).where(Document.kb_id == kb_id, Document.is_deleted == False)
    
    # 根据用户角色过滤文档
    # 1. 如果用户是知识库所有者，能看到所有文档
    # 2. 否则，只能看到与用户角色关联的文档
    kb_result = await db.execute(
        select(KnowledgeBase).where(KnowledgeBase.id == kb_id, KnowledgeBase.is_deleted == False)
    )
    kb = kb_result.scalar_one_or_none()
    
    if not kb:
        raise HTTPException(404, "知识库不存在")
    
    if kb.owner_id != user.id:
        # 用户不是所有者，需要根据角色过滤
        if user.role_id:
            # 构建子查询：获取用户角色可访问的文档
            role_stmt = select(DocumentRole.doc_id).where(
                DocumentRole.role_id == user.role_id
            )
            base_stmt = base_stmt.where(
                Document.id.in_(role_stmt)
            )
        else:
            # 没有角色的用户看不到任何文档
            base_stmt = base_stmt.where(False)
    
    # 添加文件名过滤
    if filename:
        base_stmt = base_stmt.where(Document.filename.ilike(f"%{filename}%"))
    
    # 添加创建日期过滤
    if created_from:
        try:
            from_date = datetime.fromisoformat(created_from)
            base_stmt = base_stmt.where(Document.created_at >= from_date)
        except:
            pass
    
    if created_to:
        try:
            to_date = datetime.fromisoformat(created_to)
            base_stmt = base_stmt.where(Document.created_at <= to_date)
        except:
            pass
    
    # 计算总数
    count_stmt = select(func.count()).select_from(base_stmt.subquery())
    count_result = await db.execute(count_stmt)
    total = count_result.scalar()
    
    # 添加分页
    offset = (page - 1) * page_size
    stmt = base_stmt.offset(offset).limit(page_size).order_by(Document.created_at.desc())
    
    # 执行查询
    result = await db.execute(stmt)
    docs = result.scalars().all()
    
    # 构建响应
    return Response(data={
        "data": [DocumentResponse.model_validate(d) for d in docs],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size
    })


@router.get("/{doc_id}/chunks", response_model=Response)
async def get_chunks(
    doc_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """获取文档的分块列表"""
    # 验证用户是否有权限访问该文档
    doc_result = await db.execute(
        select(Document).where(Document.id == doc_id, Document.is_deleted == False)
    )
    doc = doc_result.scalar_one_or_none()
    
    if not doc:
        raise HTTPException(404, "文档不存在")
    
    # 检查权限
    kb_result = await db.execute(
        select(KnowledgeBase).where(KnowledgeBase.id == doc.kb_id, KnowledgeBase.is_deleted == False)
    )
    kb = kb_result.scalar_one_or_none()
    
    if not kb:
        raise HTTPException(404, "知识库不存在")
    
    if kb.owner_id != user.id:
        # 用户不是所有者，需要检查角色权限
        if user.role_id:
            # 检查用户角色是否有权限访问该文档
            role_result = await db.execute(
                select(DocumentRole).where(
                    DocumentRole.doc_id == doc_id,
                    DocumentRole.role_id == user.role_id
                )
            )
            if not role_result.scalar_one_or_none():
                raise HTTPException(403, "无权限访问该文档")
        else:
            raise HTTPException(403, "无权限访问该文档")
    
    result = await db.execute(
        select(DocumentChunk)
        .where(DocumentChunk.doc_id == doc_id, DocumentChunk.is_deleted == False)
        .order_by(DocumentChunk.chunk_index)
    )
    chunks = result.scalars().all()
    return Response(data=[ChunkResponse.model_validate(c) for c in chunks])


@router.delete("/{doc_id}", response_model=Response)
async def delete_document(
    doc_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """删除文档"""
    result = await db.execute(select(Document).where(Document.id == doc_id, Document.is_deleted == False))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(404, "文档不存在")

    # 检查权限
    kb_result = await db.execute(
        select(KnowledgeBase).where(KnowledgeBase.id == doc.kb_id, KnowledgeBase.is_deleted == False)
    )
    kb = kb_result.scalar_one_or_none()
    
    if not kb:
        raise HTTPException(404, "知识库不存在")
    
    if kb.owner_id != user.id:
        raise HTTPException(403, "只有知识库所有者可以删除文档")

    # 删除向量
    vector_store.delete_by_doc(doc.kb_id, doc.id)

    # 删除文件
    if os.path.exists(doc.file_path):
        os.remove(doc.file_path)

    # 伪删除：将文档和相关的文档分块标记为已删除
    doc.is_deleted = True
    
    # 标记相关的文档分块为已删除
    await db.execute(
        update(DocumentChunk)
        .where(DocumentChunk.doc_id == doc_id)
        .values(is_deleted=True)
    )
    
    # 删除文档角色关联
    await db.execute(
        update(DocumentRole)
        .where(DocumentRole.doc_id == doc_id)
        .values(is_deleted=True)
    )

    kb_result = await db.execute(
        select(KnowledgeBase).where(KnowledgeBase.id == doc.kb_id)
    )
    kb = kb_result.scalar_one_or_none()
    if kb:
        # 重新计算，只统计未删除的文档
        count_result = await db.execute(
            select(Document).where(Document.kb_id == doc.kb_id, Document.is_deleted == False)
        )
        all_docs = count_result.scalars().all()
        kb.doc_count = len(all_docs)
        kb.chunk_count = sum(d.chunk_count for d in all_docs)

    await db.commit()
    return Response(data={"message": "已删除"})


@router.get("/{doc_id}/permissions", response_model=Response)
async def get_document_permissions(
    doc_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """获取文档的角色权限列表"""
    # 验证文档存在
    doc_result = await db.execute(
        select(Document).where(Document.id == doc_id, Document.is_deleted == False)
    )
    doc = doc_result.scalar_one_or_none()
    if not doc:
        raise HTTPException(404, "文档不存在")
    
    # 检查权限（只有知识库所有者可以管理权限）
    kb_result = await db.execute(
        select(KnowledgeBase).where(KnowledgeBase.id == doc.kb_id, KnowledgeBase.is_deleted == False)
    )
    kb = kb_result.scalar_one_or_none()
    if not kb or kb.owner_id != user.id:
        raise HTTPException(403, "只有知识库所有者可以管理文档权限")
    
    result = await db.execute(
        select(Role, DocumentRole)
        .join(DocumentRole, Role.id == DocumentRole.role_id)
        .where(
            DocumentRole.doc_id == doc_id,
            DocumentRole.is_deleted == False
        )
    )
    permissions = []
    for role, doc_role in result.all():
        permissions.append({
            "role_id": role.id,
            "role_name": role.name,
            "role_code": role.code
        })
    
    return Response(data=permissions)


@router.post("/{doc_id}/permissions", response_model=Response)
async def add_document_permission(
    doc_id: str,
    role_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """为文档添加角色权限"""
    # 验证文档存在
    doc_result = await db.execute(
        select(Document).where(Document.id == doc_id, Document.is_deleted == False)
    )
    doc = doc_result.scalar_one_or_none()
    if not doc:
        raise HTTPException(404, "文档不存在")
    
    # 检查权限（只有知识库所有者可以管理权限）
    kb_result = await db.execute(
        select(KnowledgeBase).where(KnowledgeBase.id == doc.kb_id, KnowledgeBase.is_deleted == False)
    )
    kb = kb_result.scalar_one_or_none()
    if not kb or kb.owner_id != user.id:
        raise HTTPException(403, "只有知识库所有者可以管理文档权限")
    
    # 验证角色存在
    role_result = await db.execute(
        select(Role).where(Role.id == role_id)
    )
    role = role_result.scalar_one_or_none()
    if not role:
        raise HTTPException(404, "角色不存在")
    
    # 检查是否已存在权限
    existing_result = await db.execute(
        select(DocumentRole).where(
            DocumentRole.doc_id == doc_id,
            DocumentRole.role_id == role_id,
            DocumentRole.is_deleted == False
        )
    )
    if existing_result.scalars().first():
        raise HTTPException(400, "该角色已拥有访问权限")
    
    # 检查是否存在已删除的权限记录
    deleted_result = await db.execute(
        select(DocumentRole).where(
            DocumentRole.doc_id == doc_id,
            DocumentRole.role_id == role_id,
            DocumentRole.is_deleted == True
        )
    )
    deleted_record = deleted_result.scalars().first()
    
    if deleted_record:
        # 如果存在已删除的记录，更新它
        deleted_record.is_deleted = False
        deleted_record.created_at = datetime.utcnow()
    else:
        # 否则创建新记录
        doc_role = DocumentRole(
            doc_id=doc_id,
            role_id=role_id
        )
        db.add(doc_role)
    
    await db.commit()
    
    return Response(data={"message": "权限添加成功"})


@router.delete("/{doc_id}/permissions/{role_id}", response_model=Response)
async def remove_document_permission(
    doc_id: str,
    role_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """从文档移除角色权限"""
    # 验证文档存在
    doc_result = await db.execute(
        select(Document).where(Document.id == doc_id, Document.is_deleted == False)
    )
    doc = doc_result.scalar_one_or_none()
    if not doc:
        raise HTTPException(404, "文档不存在")
    
    # 检查权限（只有知识库所有者可以管理权限）
    kb_result = await db.execute(
        select(KnowledgeBase).where(KnowledgeBase.id == doc.kb_id, KnowledgeBase.is_deleted == False)
    )
    kb = kb_result.scalar_one_or_none()
    if not kb or kb.owner_id != user.id:
        raise HTTPException(403, "只有知识库所有者可以管理文档权限")
    
    # 查找并删除权限
    result = await db.execute(
        update(DocumentRole)
        .where(
            DocumentRole.doc_id == doc_id,
            DocumentRole.role_id == role_id,
            DocumentRole.is_deleted == False
        )
        .values(is_deleted=True)
    )
    
    if result.rowcount == 0:
        raise HTTPException(404, "权限不存在")
    
    await db.commit()
    return Response(data={"message": "权限移除成功"})