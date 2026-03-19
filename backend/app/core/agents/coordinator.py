"""智能体协调器"""
from typing import List, Dict, Any, Optional
from loguru import logger


class AgentCoordinator:
    """智能体协调器"""
    
    def __init__(self, agents: Dict[str, Any]):
        """初始化协调器
        
        Args:
            agents: 智能体字典，键为智能体名称，值为智能体实例
        """
        self.agents = agents
    
    async def assign_task(self, task: str, context: Dict[str, Any]) -> str:
        """分配任务给合适的智能体
        
        Args:
            task: 任务描述
            context: 上下文信息
            
        Returns:
            分配的智能体名称
        """
        logger.info(f"[AgentCoordinator] Assigning task: {task}")
        
        # 简单的任务分配逻辑
        task_lower = task.lower()
        
        if any(keyword in task_lower for keyword in ['查询', '检索', '信息', '知识']):
            return 'research_agent'
        elif any(keyword in task_lower for keyword in ['数据库', 'sql', '数据']):
            return 'database_agent'
        elif any(keyword in task_lower for keyword in ['图', '关系', '网络']):
            return 'graph_agent'
        elif any(keyword in task_lower for keyword in ['时间', '日期', '去年', '今年']):
            return 'time_agent'
        else:
            # 默认使用研究智能体
            return 'research_agent'
    
    async def coordinate(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """协调多个智能体完成任务
        
        Args:
            task: 任务描述
            context: 上下文信息
            
        Returns:
            任务执行结果
        """
        logger.info(f"[AgentCoordinator] Coordinating task: {task}")
        
        # 分配任务
        agent_name = await self.assign_task(task, context)
        logger.info(f"[AgentCoordinator] Assigned task to {agent_name}")
        
        # 执行任务
        if agent_name in self.agents:
            agent = self.agents[agent_name]
            result = await agent.run(task, context)
            return {
                'agent': agent_name,
                'result': result
            }
        else:
            logger.error(f"[AgentCoordinator] Agent {agent_name} not found")
            return {
                'agent': None,
                'result': {
                    'success': False,
                    'error': f'智能体 {agent_name} 不存在'
                }
            }
