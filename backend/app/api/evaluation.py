"""
效果评估 API

评估算法整体逻辑和实现思路：

1. 核心评分维度：
   - 语义相似度 (0-0.4)：计算AI回答与参考答案的语义相似度，使用Sentence-BERT模型
   - 事实性评分 (0-0.3)：检测AI回答中的事实性陈述是否与知识库一致
   - 完整性评分 (0-0.1)：评估回答的长度和信息覆盖度
   - 连贯性评分 (0-0.1)：评估回答的句子结构和逻辑连贯性
   - 相关性评分 (0-0.1)：评估回答与问题的相关程度

2. 特殊情况处理：
   - 双方都未检索到：当AI回答和参考答案都表示未检索到时，给予高分(0.9)
   - AI未检索到但参考答案明确：给予中等分数(0.4)，因为AI基于实际知识库情况
   - AI未检索到且参考答案不明确：给予较高分数(0.7)
   - 语义相反：当检测到明确的相反语义时，给予低分(0.2)

3. 算法流程：
   a. 接收评估请求，包含问题、参考答案、知识库ID和模型ID
   b. 使用RAGPipeline生成AI回答
   c. 检测是否为未检索到的特殊情况
   d. 若为特殊情况，直接应用对应评分规则
   e. 若为常规情况，计算各维度评分并加权汇总
   f. 确保最终分数在0-1之间

4. 关键技术实现：
   - 语义相似度：使用Sentence-BERT模型生成嵌入向量，计算余弦相似度
   - 事实性检查：从知识库检索相关信息，验证AI回答中的事实性陈述
   - 相反语义检测：使用LLM（如OpenAI模型）检测语义相反情况
   - 多维度评分：综合考虑多个维度，加权计算最终分数

5. 性能优化：
   - 使用异步操作处理数据库查询和向量检索
   - 实现模型参数的合理传递和重用
   - 添加错误处理和降级机制

6. 扩展能力：
   - 支持按知识库ID过滤评估结果
   - 支持按问题名称模糊搜索评估结果
   - 提供评估报告生成功能
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database import get_db
from backend.app.models.user import User
from backend.app.models.knowledge_base import KnowledgeBase
from backend.app.models.evaluation import Evaluation
from backend.app.schemas.evaluation import EvalReport, EvalMetrics, EvalCreate, EvalResponse
from backend.app.utils.auth import get_current_user
from backend.app.core.evaluator import Evaluator
from backend.app.core.rag_pipeline import RAGPipeline
from backend.app.models.response_model import Response

# 添加评分所需的依赖
import numpy as np
from sentence_transformers import SentenceTransformer, util

router = APIRouter()
evaluator = Evaluator()
pipeline = RAGPipeline()

# 加载语义相似度模型
from backend.app.config import get_settings
settings = get_settings()
semantic_model = SentenceTransformer(settings.LOCAL_EMBEDDING_MODEL)

# 评分辅助函数
async def calculate_semantic_similarity(answer: str, reference: str, model=None) -> float:
    """计算语义相似度，检测语义相反的情况"""
    try:
        # 生成嵌入向量
        answer_embedding = semantic_model.encode(answer, convert_to_tensor=True)
        reference_embedding = semantic_model.encode(reference, convert_to_tensor=True)
        
        # 计算余弦相似度
        similarity = util.pytorch_cos_sim(answer_embedding, reference_embedding).item()
        
        # 检测语义相反的情况
        if similarity < 0.3:
            # 检查是否包含明确的相反语义
            if await contains_opposite_meaning(answer, reference, model):
                # 语义相反，给予很低的分数
                return 0.1
        
        # 确保相似度在0-1之间
        return max(0.0, min(1.0, similarity))
    except Exception as e:
        print(f"语义相似度计算失败: {e}")
        # 失败时返回基于关键词匹配的相似度
        return calculate_keyword_similarity(answer, reference)

async def contains_opposite_meaning(answer: str, reference: str, model=None) -> bool:
    """使用大模型检测两个文本是否包含相反的语义"""
    from openai import AsyncOpenAI
    
    # 移除引用信息
    import re
    answer_clean = re.sub(r'\（参考信息.*?\）', '', answer)
    reference_clean = re.sub(r'\（参考信息.*?\）', '', reference)
    
    # 简单的规则检查作为快速通道
    # 检查特殊情况：参考答案是"我不知道"或类似表达
    reference_lower = reference_clean.lower()
    if any(phrase in reference_lower for phrase in ['不知道', '不清楚', '不了解', '不确定']):
        # 如果参考答案表示不知道，但AI回答给出了明确的事实性陈述
        answer_lower = answer_clean.lower()
        if any(word in answer_lower for word in ['是', '有', '在', '写了', '是的', '有写', '确实', '真的', '肯定']):
            return True
    
    # 如果没有提供模型，直接使用备用方法
    if not model:
        return contains_opposite_meaning_fallback(answer_clean, reference_clean)
    
    # 使用大模型进行更复杂的语义判断
    try:
        # 配置OpenAI客户端
        client = AsyncOpenAI(
            api_key=model.api_key,
            base_url=model.base_url
        )
        
        # 构建提示
        prompt = f"""请判断以下两个文本是否包含相反的语义。

文本1: {answer_clean}
文本2: {reference_clean}

请回答"是"或"否"，并简要说明理由。

示例：
文本1: 今天天气很好
文本2: 今天天气不好
回答：是，文本1说天气很好，文本2说天气不好，语义相反。

文本1: 我喜欢苹果
文本2: 我不喜欢苹果
回答：是，文本1表示喜欢，文本2表示不喜欢，语义相反。

文本1: 他很高
文本2: 他不高
回答：是，文本1表示高，文本2表示不高，语义相反。

文本1: 今天是晴天
文本2: 今天阳光明媚
回答：否，两个文本都表示天气好，语义相同。

文本1: 我吃了早餐
文本2: 我已经吃过早饭了
回答：否，两个文本都表示吃过早餐，语义相同。

现在请判断：
"""
        
        # 调用大模型
        response = await client.chat.completions.create(
            model=model.model,
            messages=[
                {"role": "system", "content": "你是一个语义判断助手，专门判断两个文本是否包含相反的语义。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=100
        )
        
        # 提取回答
        content = response.choices[0].message.content.strip()
        
        # 检查是否包含"是"，表示相反语义
        if "是" in content.split('，')[0]:
            return True
        else:
            return False
    except Exception as e:
        print(f"大模型判断相反语义失败: {e}")
        # 失败时使用备用方法
        return contains_opposite_meaning_fallback(answer_clean, reference_clean)

def contains_opposite_meaning_fallback(answer: str, reference: str) -> bool:
    """备用的相反语义检测方法（当大模型调用失败时使用）"""
    # 转换为小写
    answer_lower = answer.lower()
    reference_lower = reference.lower()
    
    # 常见的相反意义关键词
    positive_words = ['是', '有', '在', '写了', '是的', '有写', '确实', '真的', '肯定', '会', '能', '可以']
    negative_words = ['没有', '没', '不', '未', '无', '非', '不是', '不在', '没写', '不会', '不能', '不可以']
    
    # 检查是否一个文本包含肯定词，另一个包含否定词
    has_positive_in_answer = any(word in answer_lower for word in positive_words)
    has_negative_in_answer = any(word in answer_lower for word in negative_words)
    has_positive_in_reference = any(word in reference_lower for word in positive_words)
    has_negative_in_reference = any(word in reference_lower for word in negative_words)
    
    if (has_positive_in_answer and has_negative_in_reference) or \
       (has_negative_in_answer and has_positive_in_reference):
        return True
    
    return False

def calculate_keyword_similarity(answer: str, reference: str) -> float:
    """基于关键词匹配的相似度计算（作为备选方案）"""
    answer_lower = answer.lower()
    reference_lower = reference.lower()
    
    # 提取参考答案中的关键词
    reference_words = set(reference_lower.split())
    if not reference_words:
        return 0.5
    
    # 计算匹配的关键词比例
    matched_words = reference_words.intersection(answer_lower.split())
    return len(matched_words) / len(reference_words)

def calculate_completeness(answer: str, reference: str) -> float:
    """计算完整性评分"""
    # 基于参考答案的长度和回答的长度比例
    if len(reference) == 0:
        return 1.0
    
    # 计算长度比例
    length_ratio = min(len(answer) / len(reference), 2.0) / 2.0
    
    # 检查是否包含参考答案中的关键信息
    reference_keywords = reference.lower().split()[:5]
    if reference_keywords:
        matched_keywords = sum(1 for keyword in reference_keywords if keyword in answer.lower())
        keyword_ratio = matched_keywords / len(reference_keywords)
        return (length_ratio + keyword_ratio) / 2.0
    
    return length_ratio

def calculate_coherence(answer: str) -> float:
    """计算连贯性评分"""
    # 基于回答的句子数量和长度
    sentences = answer.split('.')
    sentences = [s.strip() for s in sentences if s.strip()]
    
    if len(sentences) == 0:
        return 0.0
    
    # 句子长度变化不大，连贯性较好
    sentence_lengths = [len(s) for s in sentences]
    if len(sentence_lengths) > 1:
        std_dev = np.std(sentence_lengths)
        avg_length = np.mean(sentence_lengths)
        # 标准差与平均长度的比例越小，连贯性越好
        coherence_score = 1.0 - min(std_dev / avg_length, 1.0)
    else:
        coherence_score = 1.0
    
    # 检查是否有重复内容
    if len(answer) > 100:
        # 简单检查是否有重复的短语
        words = answer.lower().split()
        phrases = [' '.join(words[i:i+3]) for i in range(len(words)-2)]
        unique_phrases = set(phrases)
        if len(phrases) > 0:
            repetition_score = len(unique_phrases) / len(phrases)
            coherence_score = (coherence_score + repetition_score) / 2.0
    
    return coherence_score

def calculate_relevance(answer: str, query: str) -> float:
    """计算相关性评分"""
    # 计算查询与回答的语义相似度
    try:
        query_embedding = semantic_model.encode(query, convert_to_tensor=True)
        answer_embedding = semantic_model.encode(answer, convert_to_tensor=True)
        relevance = util.pytorch_cos_sim(query_embedding, answer_embedding).item()
        return max(0.0, min(1.0, relevance))
    except Exception as e:
        print(f"相关性计算失败: {e}")
        # 失败时使用关键词匹配
        query_keywords = set(query.lower().split())
        answer_keywords = set(answer.lower().split())
        if not query_keywords:
            return 0.5
        matched_keywords = query_keywords.intersection(answer_keywords)
        return len(matched_keywords) / len(query_keywords)

async def calculate_factuality(answer: str, kb_id: str, model=None) -> float:
    """计算事实性评分，检测AI回答中是否有幻觉内容"""
    from backend.app.core.vector_store import VectorStore
    from backend.app.models.model import Model
    from sqlalchemy import select
    from backend.app.database import async_session_factory

    # 提取AI回答中的事实性陈述
    factual_statements = extract_factual_statements(answer)

    if not factual_statements:
        # 没有可检查的事实性陈述，返回中等分数
        return 0.01

    # 使用异步上下文管理器获取数据库会话
    async with async_session_factory() as db:
        try:
            # 获取知识库信息，包括模型参数
            result = await db.execute(
                select(KnowledgeBase).where(KnowledgeBase.id == kb_id)
            )
            kb = result.scalar_one_or_none()

            if not kb:
                # 知识库不存在，返回0，没有参考依据
                return 0.0

            # 获取嵌入模型信息
            embedding_model = None
            if kb.embedding_model_id:
                embed_result = await db.execute(
                    select(Model).where(Model.id == kb.embedding_model_id)
                )
                embedding_model = embed_result.scalar_one_or_none()

            # 从知识库中检索相关信息，传递模型参数
            api_key = embedding_model.api_key if embedding_model else None
            base_url = embedding_model.base_url if embedding_model else None
            model_name = embedding_model.model if embedding_model else None
            vector_store = VectorStore(api_key, base_url, model_name, embedding_model)
            factuality_score = 0.0
            checked_statements = 0

            for statement in factual_statements:
                # 为每个事实性陈述从知识库中检索相关信息
                search_results = await vector_store.search(kb_id, statement, top_k=3)

                if search_results:
                    # 计算陈述与检索结果的语义相似度
                    statement_embedding = semantic_model.encode(statement, convert_to_tensor=True)
                    max_similarity = 0.0
                    has_opposite = False
                    
                    for result in search_results:
                        result_embedding = semantic_model.encode(result.content, convert_to_tensor=True)
                        similarity = util.pytorch_cos_sim(statement_embedding, result_embedding).item()
                        
                        # 检查是否有相反的信息
                        if similarity < 0.3 and await contains_opposite_meaning(statement, result.content, model):
                            has_opposite = True
                            break
                        
                        max_similarity = max(max_similarity, similarity)
                    
                    # 如果有相反的信息，降低事实性评分
                    if has_opposite:
                        factuality_score += 0.1  # 很低的分数
                    # 如果相似度高于阈值，认为陈述是事实性的
                    elif max_similarity > 0.7:
                        factuality_score += 1.0
                    checked_statements += 1

            # 计算事实性评分
            if checked_statements > 0:
                return factuality_score / checked_statements
            else:
                return 0.5
        except Exception as e:
            print(f"事实性检查失败: {e}")
            # 失败时返回基于引用的事实性评分
            return calculate_citation_based_factuality(answer)

def extract_factual_statements(text: str) -> list:
    """提取文本中的事实性陈述"""
    import re
    
    # 移除引用信息
    text = re.sub(r'\（参考信息.*?\）', '', text)
    
    # 分割句子
    sentences = re.split(r'[。！？]', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    # 提取事实性陈述（包含具体信息的句子）
    factual_statements = []
    
    # 关键词列表，用于识别事实性陈述
    factual_keywords = [
        '是', '有', '在', '位于', '属于', '包含', '包括', '由', '组成',
        '成立', '创建', '建立', '开始', '结束', '完成', '实现', '达成',
        '获得', '赢得', '取得', '具有', '拥有', '具备', '符合', '满足',
        '超过', '低于', '等于', '大于', '小于', '等于', '增加', '减少',
        '提高', '降低', '改善', '恶化', '发展', '变化', '趋势', '状况'
    ]
    
    for sentence in sentences:
        # 检查句子是否包含事实性关键词
        if any(keyword in sentence for keyword in factual_keywords):
            # 检查句子是否包含具体信息（如数字、日期、地点等）
            if re.search(r'\d+|\d{4}[-/年]\d{1,2}[-/月]\d{1,2}|[\u4e00-\u9fa5]{2,}市|[\u4e00-\u9fa5]{2,}省', sentence):
                factual_statements.append(sentence)
            # 或者长度足够长，可能包含事实性信息
            elif len(sentence) > 10:
                factual_statements.append(sentence)
    
    return factual_statements

def calculate_citation_based_factuality(answer: str) -> float:
    """基于引用的事实性评分（作为备选方案）"""
    import re
    
    # 检查是否包含引用信息
    has_citation = bool(re.search(r'参考信息', answer))
    
    # 检查回答长度和结构
    if has_citation:
        # 有引用信息，提高事实性评分
        return 0.8
    else:
        # 无引用信息，降低事实性评分
        return 0.4


@router.get("/report/{kb_id}", response_model=Response)
async def get_eval_report(
    kb_id: str,
    period: int = 30,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """获取知识库评估报告"""
    result = await db.execute(
        select(KnowledgeBase).where(KnowledgeBase.id == kb_id)
    )
    kb = result.scalar_one_or_none()
    if not kb:
        report = EvalReport(
            kb_id=kb_id, kb_name="未知", metrics=EvalMetrics(), period=f"{period}d"
        )
    else:
        report = await evaluator.generate_report(db, kb_id, kb.name, period)
    return Response(data=report)


@router.get("", response_model=Response)
async def get_evaluations(
    kb_id: str = None,
    query: str = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """获取评估列表"""
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info(f"接收到的参数: kb_id={kb_id}, query={query}")
    
    from sqlalchemy import or_
    
    db_query = select(Evaluation).order_by(Evaluation.created_at.desc())
    
    # 按知识库ID过滤
    if kb_id:
        logger.info(f"应用知识库过滤: {kb_id}")
        db_query = db_query.where(Evaluation.kb_id == kb_id)
    
    # 按问题名称过滤
    if query:
        logger.info(f"应用查询过滤: {query}")
        db_query = db_query.where(Evaluation.query.ilike(f"%{query}%"))
    
    logger.info(f"生成的SQL查询: {db_query}")
    
    result = await db.execute(db_query)
    evaluations = result.scalars().all()
    logger.info(f"查询结果数量: {len(evaluations)}")
    return Response(data=[EvalResponse.model_validate(eval) for eval in evaluations])


@router.post("", response_model=Response)
async def create_evaluation(
    eval_data: EvalCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """创建评估"""
    from backend.app.models.model import Model
    
    # 验证知识库ID
    if not eval_data.kb_ids:
        raise HTTPException(status_code=400, detail="知识库ID不能为空")
    
    # 验证模型ID
    if not eval_data.model_id:
        raise HTTPException(status_code=400, detail="模型ID不能为空")
    
    # 获取知识库信息
    kb_id = eval_data.kb_ids[0]
    result = await db.execute(
        select(KnowledgeBase).where(KnowledgeBase.id == kb_id)
    )
    kb = result.scalar_one_or_none()
    
    if not kb:
        raise HTTPException(status_code=404, detail=f"知识库 {kb_id} 不存在")
    
    # 查询嵌入模型
    embedding_model = None
    if kb.embedding_model_id:
        embed_result = await db.execute(
            select(Model).where(Model.id == kb.embedding_model_id)
        )
        embedding_model = embed_result.scalar_one_or_none()
    
    # 查询重排序模型
    rerank_model = None
    if kb.rerank_model_id:
        rerank_result = await db.execute(
            select(Model).where(Model.id == kb.rerank_model_id)
        )
        rerank_model = rerank_result.scalar_one_or_none()
    
    # 查询聊天模型
    chat_model_result = await db.execute(
        select(Model).where(Model.id == eval_data.model_id)
    )
    chat_model = chat_model_result.scalar_one_or_none()
    
    if not chat_model:
        raise HTTPException(status_code=404, detail=f"模型 {eval_data.model_id} 不存在")
    
    # 使用知识库的模型信息初始化 RAG 管道
    rag_pipeline = RAGPipeline(
        api_key=chat_model.api_key,
        base_url=chat_model.base_url,
        model_name=chat_model.model,
        embedding_model=embedding_model,
        rerank_model=rerank_model
    )
    
    # 使用 RAG 生成回答
    rag_result = await rag_pipeline.run(
        query=eval_data.query,
        kb_ids=eval_data.kb_ids,
        retrieval_mode=kb.retrieval_mode,
        model=chat_model.model,
        model_id=chat_model.id,
        api_key=chat_model.api_key,
        base_url=chat_model.base_url
    )
    
    # 多维度评分逻辑
    rag_answer = rag_result.answer
    score = 0.0
    
    if rag_answer:
        # 检查是否为未检索到相关内容的情况
        no_retrieval_answer = any(phrase in rag_answer for phrase in ['未检索到', '未找到', '没有找到', '没有相关'])
        no_retrieval_reference = any(phrase in eval_data.reference_answer for phrase in ['未检索到', '未找到', '没有找到', '没有相关'])
        
        # 特殊情况处理：双方都未检索到
        if no_retrieval_answer and no_retrieval_reference:
            # 双方都未检索到，给予很高的分数
            score = 0.9
        # 特殊情况处理：AI未检索到，但参考答案是明确的
        elif no_retrieval_answer and not no_retrieval_reference:
            # 检查参考答案是否是明确的肯定或否定
            reference_lower = eval_data.reference_answer.lower()
            has_explicit_answer = any(word in reference_lower for word in ['在', '有', '是', '写了', '没在', '没有', '不是', '没写'])
            
            if has_explicit_answer:
                # AI未检索到，但参考答案明确，给予中等分数
                # 因为AI的回答是基于知识库的，可能知识库确实没有相关信息
                score = 0.4
            else:
                # 参考答案也不明确，给予较高分数
                score = 0.7
        else:
            # 常规评分逻辑
            # 检查是否存在明确的相反语义
            has_opposite_meaning = await contains_opposite_meaning(rag_answer, eval_data.reference_answer, chat_model)
            
            if has_opposite_meaning:
                # 明确的相反语义，直接给予很低的分数
                score = 0.2
            else:
                # 1. 语义相似度评分 (0-0.4)
                semantic_score = await calculate_semantic_similarity(rag_answer, eval_data.reference_answer, chat_model)
                score += semantic_score * 0.4
                
                # 2. 事实性评分 (0-0.3)
                factuality_score = await calculate_factuality(rag_answer, kb_id, chat_model)
                score += factuality_score * 0.3
                
                # 3. 完整性评分 (0-0.1)
                completeness_score = calculate_completeness(rag_answer, eval_data.reference_answer)
                score += completeness_score * 0.1
                
                # 4. 连贯性评分 (0-0.1)
                coherence_score = calculate_coherence(rag_answer)
                score += coherence_score * 0.1
                
                # 5. 相关性评分 (0-0.1)
                relevance_score = calculate_relevance(rag_answer, eval_data.query)
                score += relevance_score * 0.1
    
    # 确保分数在0-1之间
    score = min(1.0, max(0.0, score))
    
    # 创建评估记录
    evaluation = Evaluation(
        query=eval_data.query,
        reference_answer=eval_data.reference_answer,
        rag_answer=rag_answer,
        score=min(1.0, score),
        kb_id=eval_data.kb_ids[0],
        model_id=eval_data.model_id
    )
    
    db.add(evaluation)
    await db.commit()
    await db.refresh(evaluation)
    
    return Response(data=EvalResponse.model_validate(evaluation))


@router.put("/{eval_id}", response_model=Response)
async def update_evaluation(
    eval_id: int,
    eval_data: EvalCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """更新评估（重新评估）"""
    from backend.app.models.model import Model
    
    # 验证知识库ID
    if not eval_data.kb_ids:
        raise HTTPException(status_code=400, detail="知识库ID不能为空")
    
    # 验证模型ID
    if not eval_data.model_id:
        raise HTTPException(status_code=400, detail="模型ID不能为空")
    
    # 获取知识库信息
    kb_id = eval_data.kb_ids[0]
    result = await db.execute(
        select(KnowledgeBase).where(KnowledgeBase.id == kb_id)
    )
    kb = result.scalar_one_or_none()
    
    if not kb:
        raise HTTPException(status_code=404, detail=f"知识库 {kb_id} 不存在")
    
    # 查询嵌入模型
    embedding_model = None
    if kb.embedding_model_id:
        embed_result = await db.execute(
            select(Model).where(Model.id == kb.embedding_model_id)
        )
        embedding_model = embed_result.scalar_one_or_none()
    
    # 查询重排序模型
    rerank_model = None
    if kb.rerank_model_id:
        rerank_result = await db.execute(
            select(Model).where(Model.id == kb.rerank_model_id)
        )
        rerank_model = rerank_result.scalar_one_or_none()
    
    # 查询聊天模型
    chat_model_result = await db.execute(
        select(Model).where(Model.id == eval_data.model_id)
    )
    chat_model = chat_model_result.scalar_one_or_none()
    
    if not chat_model:
        raise HTTPException(status_code=404, detail=f"模型 {eval_data.model_id} 不存在")
    
    # 使用知识库的模型信息初始化 RAG 管道
    rag_pipeline = RAGPipeline(
        api_key=chat_model.api_key,
        base_url=chat_model.base_url,
        model_name=chat_model.model,
        embedding_model=embedding_model,
        rerank_model=rerank_model
    )
    
    # 使用 RAG 生成回答
    rag_result = await rag_pipeline.run(
        query=eval_data.query,
        kb_ids=eval_data.kb_ids,
        retrieval_mode=kb.retrieval_mode,
        model=chat_model.model,
        model_id=chat_model.id,
        api_key=chat_model.api_key,
        base_url=chat_model.base_url
    )
    
    # 多维度评分逻辑
    rag_answer = rag_result.answer
    score = 0.0
    
    if rag_answer:
        # 检查是否为未检索到相关内容的情况
        no_retrieval_answer = any(phrase in rag_answer for phrase in ['未检索到', '未找到', '没有找到', '没有相关'])
        no_retrieval_reference = any(phrase in eval_data.reference_answer for phrase in ['未检索到', '未找到', '没有找到', '没有相关'])
        
        # 特殊情况处理：双方都未检索到
        if no_retrieval_answer and no_retrieval_reference:
            # 双方都未检索到，给予很高的分数
            score = 0.9
        # 特殊情况处理：AI未检索到，但参考答案是明确的
        elif no_retrieval_answer and not no_retrieval_reference:
            # 检查参考答案是否是明确的肯定或否定
            reference_lower = eval_data.reference_answer.lower()
            has_explicit_answer = any(word in reference_lower for word in ['在', '有', '是', '写了', '没在', '没有', '不是', '没写'])
            
            if has_explicit_answer:
                # AI未检索到，但参考答案明确，给予中等分数
                # 因为AI的回答是基于知识库的，可能知识库确实没有相关信息
                score = 0.4
            else:
                # 参考答案也不明确，给予较高分数
                score = 0.7
        else:
            # 常规评分逻辑
            # 检查是否存在明确的相反语义
            has_opposite_meaning = await contains_opposite_meaning(rag_answer, eval_data.reference_answer, chat_model)
            
            if has_opposite_meaning:
                # 明确的相反语义，直接给予很低的分数
                score = 0.2
            else:
                # 1. 语义相似度评分 (0-0.4)
                semantic_score = await calculate_semantic_similarity(rag_answer, eval_data.reference_answer, chat_model)
                score += semantic_score * 0.4
                
                # 2. 事实性评分 (0-0.3)
                factuality_score = await calculate_factuality(rag_answer, kb_id, chat_model)
                score += factuality_score * 0.3
                
                # 3. 完整性评分 (0-0.1)
                completeness_score = calculate_completeness(rag_answer, eval_data.reference_answer)
                score += completeness_score * 0.1
                
                # 4. 连贯性评分 (0-0.1)
                coherence_score = calculate_coherence(rag_answer)
                score += coherence_score * 0.1
                
                # 5. 相关性评分 (0-0.1)
                relevance_score = calculate_relevance(rag_answer, eval_data.query)
                score += relevance_score * 0.1
    
    # 确保分数在0-1之间
    score = min(1.0, max(0.0, score))
    
    # 获取现有评估
    result = await db.execute(select(Evaluation).where(Evaluation.id == eval_id))
    evaluation = result.scalar_one_or_none()
    
    if not evaluation:
        raise HTTPException(status_code=404, detail="评估不存在")
    
    # 更新评估记录
    evaluation.query = eval_data.query
    evaluation.reference_answer = eval_data.reference_answer
    evaluation.rag_answer = rag_answer
    evaluation.score = min(1.0, score)
    evaluation.kb_id = eval_data.kb_ids[0]
    evaluation.model_id = eval_data.model_id
    
    await db.commit()
    await db.refresh(evaluation)
    
    return Response(data=EvalResponse.model_validate(evaluation))


@router.delete("/{eval_id}", response_model=Response)
async def delete_evaluation(
    eval_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """删除评估"""
    result = await db.execute(select(Evaluation).where(Evaluation.id == eval_id))
    evaluation = result.scalar_one_or_none()
    
    if not evaluation:
        raise HTTPException(status_code=404, detail="评估不存在")
    
    await db.delete(evaluation)
    await db.commit()
    
    return Response(data={"message": "评估已删除"})
