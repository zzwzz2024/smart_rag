"""
文档管理 API
"""
import os
import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.database import get_db, async_session_factory
from backend.app.models.user import User
from backend.app.models.document import Document, DocumentChunk
from backend.app.models.knowledge_base import KnowledgeBase
from backend.app.models.model import Model
from backend.app.schemas.document import DocumentResponse, ChunkResponse
from backend.app.utils.auth import get_current_user
from backend.app.services.doc_service import process_document
from backend.app.core.vector_store import VectorStore
from backend.app.config import get_settings
import backend.app.services.chat_service as chat_service
from backend.app.core.rag_pipeline import RAGPipeline
from backend.app.models.response_model import Response

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
        select(KnowledgeBase).where(KnowledgeBase.id == kb_id)
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
        select(KnowledgeBase).where(KnowledgeBase.id == kb_id)
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
    from sqlalchemy import or_, and_, func
    from datetime import datetime
    
    # 构建查询
    stmt = select(Document).where(Document.kb_id == kb_id)
    
    # 添加文件名过滤
    if filename:
        stmt = stmt.where(Document.filename.ilike(f"%{filename}%"))
    
    # 添加创建日期过滤
    if created_from:
        try:
            from_date = datetime.fromisoformat(created_from)
            stmt = stmt.where(Document.created_at >= from_date)
        except:
            pass
    
    if created_to:
        try:
            to_date = datetime.fromisoformat(created_to)
            stmt = stmt.where(Document.created_at <= to_date)
        except:
            pass
    
    # 计算总数
    count_stmt = select(func.count()).select_from(stmt.subquery())
    count_result = await db.execute(count_stmt)
    total = count_result.scalar()
    
    # 添加分页
    offset = (page - 1) * page_size
    stmt = stmt.offset(offset).limit(page_size).order_by(Document.created_at.desc())
    
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
    result = await db.execute(
        select(DocumentChunk)
        .where(DocumentChunk.doc_id == doc_id)
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
    result = await db.execute(select(Document).where(Document.id == doc_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(404, "文档不存在")

    # 删除向量
    vector_store.delete_by_doc(doc.kb_id, doc.id)

    # 删除文件
    if os.path.exists(doc.file_path):
        os.remove(doc.file_path)

    await db.delete(doc)
    return Response(data={"message": "已删除"})