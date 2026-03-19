"""智能体基类"""
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod


class BaseAgent(ABC):
    """智能体基类"""
    
    def __init__(self, rag_pipeline, tools=None):
        self.rag_pipeline = rag_pipeline
        self.tools = tools or []
    
    @abstractmethod
    async def plan(self, task: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """规划任务执行步骤
        
        Args:
            task: 任务描述
            context: 上下文信息
            
        Returns:
            任务执行计划
        """
        pass
    
    @abstractmethod
    async def execute(self, plan: List[Dict[str, Any]], context: Dict[str, Any]) -> Dict[str, Any]:
        """执行任务计划
        
        Args:
            plan: 任务执行计划
            context: 上下文信息
            
        Returns:
            执行结果
        """
        pass
    
    @abstractmethod
    async def reflect(self, result: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """反思执行结果，调整策略
        
        Args:
            result: 执行结果
            context: 上下文信息
            
        Returns:
            反思结果
        """
        pass
    
    async def run(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """完整执行流程
        
        Args:
            task: 任务描述
            context: 上下文信息
            
        Returns:
            最终结果
        """
        plan = await self.plan(task, context)
        result = await self.execute(plan, context)
        reflection = await self.reflect(result, context)
        return reflection
