"""
领域策略模块
"""

from .music_strategy import music_strategy
from .law_strategy import law_strategy
from .tech_strategy import tech_strategy
from .project_strategy import project_strategy
from .regulation_strategy import regulation_strategy

# 领域策略映射
domain_strategies = {
    "音乐": music_strategy,
    "法律法规": law_strategy,
    "技术文档": tech_strategy,
    "项目管理": project_strategy,
    "规章制度": regulation_strategy
}

# 默认策略
default_strategy = {
    "mode": "hybrid",
    "vector_weight": 0.6,
    "keyword_weight": 0.4,
    "top_k": 10,
    "use_expanded_query": True
}
