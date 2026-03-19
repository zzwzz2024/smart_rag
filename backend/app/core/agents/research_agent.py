"""研究智能体"""
from typing import List, Dict, Any, Optional
from backend.app.core.agents.base_agent import BaseAgent
from loguru import logger


class ResearchAgent(BaseAgent):
    """研究智能体，专注于信息检索和分析"""
    
    async def plan(self, task: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """规划任务执行步骤
        
        Args:
            task: 任务描述
            context: 上下文信息
            
        Returns:
            任务执行计划
        """
        logger.info(f"[ResearchAgent] Planning task: {task}")
        
        # 提取知识库ID
        kb_ids = context.get('kb_ids', [])
        
        # 生成执行计划
        plan = [
            {
                'step': 1,
                'action': 'retrieve_information',
                'description': '检索相关信息',
                'params': {
                    'query': task,
                    'kb_ids': kb_ids
                }
            },
            {
                'step': 2,
                'action': 'analyze_information',
                'description': '分析检索到的信息',
                'params': {
                    'query': task
                }
            },
            {
                'step': 3,
                'action': 'generate_response',
                'description': '生成最终响应',
                'params': {
                    'query': task
                }
            }
        ]
        
        return plan
    
    async def execute(self, plan: List[Dict[str, Any]], context: Dict[str, Any]) -> Dict[str, Any]:
        """执行任务计划
        
        Args:
            plan: 任务执行计划
            context: 上下文信息
            
        Returns:
            执行结果
        """
        logger.info(f"[ResearchAgent] Executing plan with {len(plan)} steps")
        
        results = {}
        
        for step in plan:
            logger.info(f"[ResearchAgent] Executing step {step['step']}: {step['description']}")
            
            if step['action'] == 'retrieve_information':
                # 使用RAG pipeline检索信息
                rag_result = await self.rag_pipeline.run(
                    query=step['params']['query'],
                    kb_ids=step['params']['kb_ids'],
                    model=context.get('model'),
                    model_id=context.get('model_id'),
                    api_key=context.get('api_key'),
                    base_url=context.get('base_url')
                )
                results['retrieved_information'] = {
                    'answer': rag_result.answer,
                    'citations': rag_result.citations,
                    'confidence': rag_result.confidence
                }
            
            elif step['action'] == 'analyze_information':
                # 分析检索到的信息
                results['analysis'] = {
                    'summary': results['retrieved_information']['answer'],
                    'confidence': results['retrieved_information']['confidence']
                }
            
            elif step['action'] == 'generate_response':
                # 生成最终响应
                results['final_response'] = results['analysis']['summary']
        
        return results
    
    async def reflect(self, result: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """反思执行结果，调整策略
        
        Args:
            result: 执行结果
            context: 上下文信息
            
        Returns:
            反思结果
        """
        logger.info(f"[ResearchAgent] Reflecting on result")
        
        # 检查执行结果
        if 'final_response' in result:
            reflection = {
                'success': True,
                'response': result['final_response'],
                'confidence': result.get('analysis', {}).get('confidence', 0.0),
                'suggestions': []
            }
            
            # 如果置信度低，添加改进建议
            if reflection['confidence'] < 0.5:
                reflection['suggestions'].append('信息检索结果置信度较低，建议使用更具体的查询词')
                reflection['suggestions'].append('考虑使用多个知识库进行交叉验证')
        else:
            reflection = {
                'success': False,
                'error': '执行过程中出现错误',
                'suggestions': ['检查知识库连接', '确认查询参数是否正确']
            }
        
        return reflection
