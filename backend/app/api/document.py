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
from backend.app.schemas.document import DocumentResponse, ChunkResponse
from backend.app.utils.auth import get_current_user
from backend.app.services.doc_service import process_document
from backend.app.core.vector_store import VectorStore
from backend.app.config import get_settings

router = APIRouter()
settings = get_settings()
vector_store = VectorStore()


@router.post("/upload/{kb_id}", response_model=DocumentResponse)
async def upload_document(
    kb_id: str,
    background_tasks: BackgroundTasks,
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

    # 创建文档记录
    doc = Document(
        id=file_id,
        kb_id=kb_id,
        filename=file.filename,
        file_path=file_path,
        file_type=ext.lstrip("."),
        file_size=len(content),
        status="pending",
    )
    db.add(doc)
    await db.flush()
    await db.commit()

    # 后台异步处理文档
    background_tasks.add_task(_process_doc_background, file_id)

    return DocumentResponse.model_validate(doc)


async def _process_doc_background(doc_id: str):
    print(f"Starting background processing for document {doc_id}")
    try:
        async with async_session_factory() as db:
            await process_document(db, doc_id)
            await db.commit()
            print(f"Document {doc_id} processed successfully")
    except Exception as e:
        print(f"Error processing document {doc_id}: {e}")
        raise

@router.get("/list/{kb_id}", response_model=dict)
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
    return {
        "data": [DocumentResponse.model_validate(d) for d in docs],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size
    }


@router.get("/{doc_id}/chunks", response_model=List[ChunkResponse])
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
    return [ChunkResponse.model_validate(c) for c in chunks]


@router.delete("/{doc_id}")
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
    return {"message": "已删除"}