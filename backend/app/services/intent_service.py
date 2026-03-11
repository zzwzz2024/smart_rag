"""
意图识别服务
"""
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.models.knowledge_base import KnowledgeBase
from backend.app.models.tag import Tag
from backend.app.models.domain import Domain


class IntentService:
    """
    意图识别服务
    """
    
    def __init__(self, db: AsyncSession, user_id: str):
        """
        初始化意图识别服务
        
        Args:
            db: 数据库会话
            user_id: 用户ID
        """
        self.db = db
        self.user_id = user_id
    
    async def match_knowledge_bases(self, query: str) -> List[str]:
        """
        匹配知识库
        
        Args:
            query: 用户查询
            
        Returns:
            List[str]: 匹配的知识库ID列表
        """
        # 1. 获取用户的所有知识库
        kbs = await self._get_user_knowledge_bases()
        
        if not kbs:
            return []
        
        # 2. 使用大模型进行意图识别和知识库匹配
        matched_kbs = await self._match_kbs_with_llm(query, kbs)
        
        return [kb.id for kb in matched_kbs]
    
    async def _get_user_knowledge_bases(self) -> List[KnowledgeBase]:
        """
        获取用户的所有知识库
        
        Returns:
            List[KnowledgeBase]: 知识库列表
        """
        result = await self.db.execute(
            select(KnowledgeBase)
            .options(
                selectinload(KnowledgeBase.tags),
                selectinload(KnowledgeBase.domains)
            )
            .where(KnowledgeBase.owner_id == self.user_id)
        )
        return result.scalars().all()
    
    def _extract_keywords(self, query: str) -> List[str]:
        """
        提取关键词
        
        Args:
            query: 用户查询
            
        Returns:
            List[str]: 关键词列表
        """
        # 直接使用大模型进行关键词提取
        # 这里简化处理，实际项目中可以调用大模型API
        import re
        # 移除标点符号
        query = re.sub(r'[\s\W]+', ' ', query)
        # 分词
        keywords = query.lower().split()
        # 去重
        keywords = list(set(keywords))
        return keywords
    
    async def _match_kbs(self, kbs: List[KnowledgeBase], keywords: List[str]) -> List[KnowledgeBase]:
        """
        匹配知识库
        
        Args:
            kbs: 知识库列表
            keywords: 关键词列表
            
        Returns:
            List[KnowledgeBase]: 匹配的知识库列表
        """
        matched_kbs = []
        
        for kb in kbs:
            # 计算匹配分数
            score = await self._calculate_match_score(kb, keywords)
            if score > 0:
                matched_kbs.append((kb, score))
        
        # 按分数排序，返回前3个匹配的知识库
        matched_kbs.sort(key=lambda x: x[1], reverse=True)
        return [kb for kb, _ in matched_kbs[:3]]
    
    async def _match_kbs_with_llm(self, query: str, kbs: List[KnowledgeBase]) -> List[KnowledgeBase]:
        """
        使用大模型进行意图识别和知识库匹配
        
        Args:
            query: 用户查询
            kbs: 知识库列表
            
        Returns:
            List[KnowledgeBase]: 匹配的知识库列表
        """
        from backend.app.core.generator import Generator
        from backend.app.models.model import Model
        from sqlalchemy import select
        
        try:
            # 获取默认的聊天模型
            model_result = await self.db.execute(
                select(Model).where(Model.type == "chat", Model.is_active == True).limit(1)
            )
            chat_model = model_result.scalar_one_or_none()
            
            # 如果没有找到聊天模型，使用关键词匹配作为兜底
            if not chat_model:
                keywords = self._extract_keywords(query)
                return await self._match_kbs(kbs, keywords)
            
            # 构建知识库信息
            kb_info = []
            for kb in kbs:
                tags = [tag.name for tag in kb.tags]
                domains = [domain.name for domain in kb.domains]
                kb_info.append({
                    "id": kb.id,
                    "name": kb.name,
                    "description": kb.description,
                    "tags": tags,
                    "domains": domains
                })
            
            # 构建提示词
            prompt = f"""
            你是一个智能助手，需要根据用户的查询和知识库信息，匹配最相关的知识库。
            
            用户查询:
            {query}
            
            可用知识库:
            {kb_info}
            
            请分析用户查询的意图，然后返回最相关的知识库ID列表，按相关性从高到低排序。
            只返回知识库ID，每个ID占一行，不要包含其他内容。
            """
            
            # 使用大模型生成匹配结果
            generator = Generator(
                api_key=chat_model.api_key,
                base_url=chat_model.base_url
            )
            response = await generator.generate(
                query=prompt,
                retrieved_chunks=[],
                conversation_history=[],
                model=chat_model.model
            )
            
            # 解析大模型的响应
            kb_ids = []
            for line in response.answer.strip().split('\n'):
                line = line.strip()
                if line:
                    kb_ids.append(line)
            
            # 根据大模型返回的ID列表，构建匹配的知识库列表
            matched_kbs = []
            for kb_id in kb_ids:
                for kb in kbs:
                    if kb.id == kb_id:
                        matched_kbs.append(kb)
                        break
            
            # 如果大模型没有返回匹配结果，使用简单的关键词匹配作为兜底
            if not matched_kbs:
                keywords = self._extract_keywords(query)
                matched_kbs = await self._match_kbs(kbs, keywords)
            
            return matched_kbs
        except Exception as e:
            # 如果使用大模型失败，使用关键词匹配作为兜底
            print(f"使用大模型进行意图识别失败: {e}")
            keywords = self._extract_keywords(query)
            return await self._match_kbs(kbs, keywords)

    async def _calculate_match_score(self, kb: KnowledgeBase, keywords: List[str]) -> float:
        """
        计算匹配分数
        
        Args:
            kb: 知识库
            keywords: 关键词列表
            
        Returns:
            float: 匹配分数
        """
        score = 0.0
        
        # 1. 匹配知识库名称和描述
        kb_text = f"{kb.name} {kb.description}".lower()
        for keyword in keywords:
            if keyword in kb_text:
                score += 1.0
        
        # 2. 匹配标签
        for tag in kb.tags:
            tag_text = f"{tag.name}".lower()
            for keyword in keywords:
                if keyword in tag_text:
                    score += 0.8
        
        # 3. 匹配领域
        for domain in kb.domains:
            domain_text = f"{domain.name} {domain.description}".lower()
            for keyword in keywords:
                if keyword in domain_text:
                    score += 0.6
        
        return score


# 导入selectinload
from sqlalchemy.orm import selectinload