"""
提示词配置模块
"""
from backend.app.core.prompts.intent_detection import INTENT_DETECTION_PROMPT
from backend.app.core.prompts.sql_generation import SQL_GENERATION_PROMPT
from backend.app.core.prompts.cypher_generation import CYPHER_GENERATION_PROMPT
from backend.app.core.prompts.query_rewriting import QUERY_REWRITING_PROMPT
from backend.app.core.prompts.data_analysis import DATABASE_ANALYSIS_PROMPT, GRAPH_DATABASE_ANALYSIS_PROMPT
from backend.app.core.prompts.generator import GENERATOR_PROMPT, RELEVANCE_JUDGMENT_PROMPT
from backend.app.core.prompts.evaluation import SEMANTIC_OPPOSITE_PROMPT
from backend.app.core.prompts.reranker import RERANKER_PROMPT
from backend.app.core.prompts.knowledge_base_matching import KNOWLEDGE_BASE_MATCHING_PROMPT

__all__ = [
    "INTENT_DETECTION_PROMPT",
    "SQL_GENERATION_PROMPT",
    "CYPHER_GENERATION_PROMPT",
    "QUERY_REWRITING_PROMPT",
    "DATABASE_ANALYSIS_PROMPT",
    "GRAPH_DATABASE_ANALYSIS_PROMPT",
    "GENERATOR_PROMPT",
    "RELEVANCE_JUDGMENT_PROMPT",
    "SEMANTIC_OPPOSITE_PROMPT",
    "RERANKER_PROMPT",
    "KNOWLEDGE_BASE_MATCHING_PROMPT",
]
