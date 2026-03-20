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
        
        # 检查是否已经处理过时间信息
        if context.get('processed_query'):
            # 如果已经处理过时间信息，根据实际查询内容分配
            processed_query = context['processed_query'].lower()
            if any(keyword in processed_query for keyword in ['数据库', 'sql', '数据', '项目', '有几个', '多少']):
                return 'database_agent'
            elif any(keyword in processed_query for keyword in ['图', '关系', '网络']):
                return 'graph_agent'
            elif any(keyword in processed_query for keyword in ['查询', '检索', '信息', '知识']):
                return 'research_agent'
            else:
                return 'research_agent'
        else:
            # 首次分配任务
            if any(keyword in task_lower for keyword in ['数据库', 'sql', '数据', '项目', '有几个', '多少']) and any(keyword in task_lower for keyword in ['时间', '日期', '去年', '今年', '上个月', '下个月']):
                # 如果同时包含数据库和时间相关内容，先分配给时间智能体处理
                return 'time_agent'
            elif any(keyword in task_lower for keyword in ['数据库', 'sql', '数据', '项目', '有几个', '多少']):
                return 'database_agent'
            elif any(keyword in task_lower for keyword in ['图', '关系', '网络']):
                return 'graph_agent'
            elif any(keyword in task_lower for keyword in ['时间', '日期', '去年', '今年', '上个月', '下个月']):
                return 'time_agent'
            elif any(keyword in task_lower for keyword in ['查询', '检索', '信息', '知识']):
                return 'research_agent'
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
            logger.info(f"[AgentCoordinator] Running agent: {agent_name}")
            result = await agent.run(task, context)
            logger.info(f"[AgentCoordinator] Agent {agent_name} completed with result: {result}")
            
            # 检查是否需要重新分配任务（如时间智能体处理后需要传递给数据库智能体）
            if agent_name == 'time_agent' and result.get('processed_query'):
                logger.info(f"[AgentCoordinator] TimeAgent processed query, reassigning: {result['processed_query']}")
                # 构建新的上下文，包含处理后的查询
                new_context = context.copy()
                new_context['processed_query'] = result['processed_query']
                # 重新分配任务
                new_agent_name = await self.assign_task(result['processed_query'], new_context)
                logger.info(f"[AgentCoordinator] Reassigned task to {new_agent_name}")
                
                if new_agent_name != 'time_agent' and new_agent_name in self.agents:
                    new_agent = self.agents[new_agent_name]
                    logger.info(f"[AgentCoordinator] Running new agent: {new_agent_name}")
                    new_result = await new_agent.run(result['processed_query'], new_context)
                    logger.info(f"[AgentCoordinator] New agent {new_agent_name} completed with result: {new_result}")
                    return {
                        'agent': new_agent_name,
                        'result': new_result
                    }
            
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
