"""
API文档下载接口
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger
from backend.app.database import get_db
from backend.app.models.user import User
from backend.app.services.api_authorization_service import ApiAuthorizationService
from backend.app.utils.auth import get_current_user
from backend.app.models.response_model import Response
from backend.app.config import get_settings
from backend.app.utils.api_utils import get_template_path, generate_api_doc_filename
import re
import urllib.parse


router = APIRouter()
settings = get_settings()


@router.get("/{authorization_id}")
async def download_api_doc(
    authorization_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """下载接口文档"""
    try:
        # 获取授权信息
        authorization = await ApiAuthorizationService.get_authorization_by_id(
            db, authorization_id
        )
        if not authorization:
            raise HTTPException(status_code=404, detail="授权不存在")
        
        # 获取授权的知识库信息
        from sqlalchemy import select, join
        from backend.app.models.knowledge_base import KnowledgeBase
        from backend.app.models.api_authorization import knowledge_base_authorization_association
        
        result = await db.execute(
            select(
                KnowledgeBase.id,
                KnowledgeBase.name
            ).select_from(
                join(
                    knowledge_base_authorization_association,
                    KnowledgeBase,
                    knowledge_base_authorization_association.c.knowledge_base_id == KnowledgeBase.id
                )
            ).where(
                knowledge_base_authorization_association.c.authorization_id == authorization_id
            )
        )
        
        knowledge_bases = []
        for kb_id, kb_name in result.all():
            knowledge_bases.append({"id": kb_id, "name": kb_name})
        
        # 读取接口文档模板
        template_path = get_template_path(settings.API_DOC_TEMPLATE_PATH)  # 使用工具函数获取模板路径
        try:
            with open(template_path, "r", encoding="utf-8") as f:
                template_content = f.read()
        except FileNotFoundError:
            raise HTTPException(status_code=500, detail="接口文档模板文件不存在")
        
        # 生成授权内容表格
        auth_table = "| 序号 | 授权厂商  | 授权码 | 知识库ID | 知识库名称  | 授权码有效期  | \n"
        auth_table += "|------|------|------|------|------|------|\n"
        
        for i, kb in enumerate(knowledge_bases, 1):
            auth_table += f"| {i} | {authorization.vendor_name} | {authorization.auth_code} | {kb['id']} | {kb['name']} | {authorization.start_time.strftime('%Y-%m-%d')}至{authorization.end_time.strftime('%Y-%m-%d')} |\n"
        
        # 替换模板中的授权内容
        updated_content = re.sub(
            r"### 2\.2 授权内容[\s\S]*?(?=## 3\. 授权验证接口)",
            f"### 2.2 授权内容\n{auth_table}",
            template_content
        )
        
        # 生成文件名
        filename = generate_api_doc_filename(authorization.vendor_name)  # 使用工具函数生成文件名
        
        # 返回文件
        # 将内容转换为UTF-8编码的字节
        content_bytes = updated_content.encode('utf-8')
        # 对文件名进行URL编码，处理中文字符
        encoded_filename = urllib.parse.quote(filename)
        return Response(
            content=content_bytes,
            media_type="text/markdown; charset=utf-8",
            headers={
                "Content-Disposition": f"attachment; filename={encoded_filename}; filename*=UTF-8''{encoded_filename}"
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"下载接口文档失败: {str(e)}")
        raise HTTPException(status_code=500, detail="下载接口文档失败")
