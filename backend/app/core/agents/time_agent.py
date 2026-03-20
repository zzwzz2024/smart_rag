"""时间智能体"""
from typing import List, Dict, Any, Optional
from backend.app.core.agents.base_agent import BaseAgent
from loguru import logger


class TimeAgent(BaseAgent):
    """时间智能体，专注于时间相关的查询和处理"""
    
    async def plan(self, task: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """规划任务执行步骤
        
        Args:
            task: 任务描述
            context: 上下文信息
            
        Returns:
            任务执行计划
        """
        logger.info(f"[TimeAgent] Planning task: {task}")
        
        # 生成执行计划
        plan = [
            {
                'step': 1,
                'action': 'extract_time',
                'description': '提取查询中的时间信息',
                'params': {
                    'query': task
                }
            },
            {
                'step': 2,
                'action': 'process_time',
                'description': '处理相对时间，转换为具体时间',
                'params': {
                    'query': task
                }
            },
            {
                'step': 3,
                'action': 'format_response',
                'description': '格式化时间信息，生成响应',
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
        logger.info(f"[TimeAgent] Executing plan with {len(plan)} steps")
        
        results = {}
        
        for step in plan:
            logger.info(f"[TimeAgent] Executing step {step['step']}: {step['description']}")
            
            if step['action'] == 'extract_time':
                # 提取查询中的时间信息
                try:
                    from backend.app.utils.time_tool import extract_time_from_query
                    time_info = extract_time_from_query(step['params']['query'])
                    results['time_info'] = time_info
                except Exception as e:
                    logger.error(f"Time extraction failed: {e}")
                    results['error'] = f'时间信息提取失败: {str(e)}'
            
            elif step['action'] == 'process_time':
                # 处理相对时间，转换为具体时间
                try:
                    from backend.app.utils.time_tool import replace_relative_time_in_query
                    processed_query = replace_relative_time_in_query(step['params']['query'])
                    results['processed_query'] = processed_query
                except Exception as e:
                    logger.error(f"Time processing failed: {e}")
                    results['error'] = f'时间处理失败: {str(e)}'
            
            elif step['action'] == 'format_response':
                # 格式化时间信息，生成响应
                if 'processed_query' in results:
                    # 检查是否需要进一步处理（如数据库查询）
                    query = step['params']['query']
                    processed_query = results['processed_query']
                    
                    # 对于包含数据库相关内容的查询，只返回处理后的查询，由协调器重新分配
                    if any(keyword in query.lower() for keyword in ['项目', '数据库', '数据', '有几个', '多少']):
                        logger.info(f"[TimeAgent] Detected database-related query, returning processed query: {processed_query}")
                        # 时间处理完成，由协调器重新分配任务
                        results['final_response'] = f"时间处理完成，正在查询数据库..."
                    else:
                        # 否则返回时间处理结果
                        results['final_response'] = self._format_time_response(
                            query,
                            processed_query,
                            results.get('time_info', {})
                        )
                else:
                    results['final_response'] = '时间处理失败'
        
        return results
    
    def _format_time_response(self, original_query: str, processed_query: str, time_info: Dict) -> str:
        """格式化时间响应
        
        Args:
            original_query: 原始查询
            processed_query: 处理后的查询
            time_info: 时间信息
            
        Returns:
            格式化后的响应
        """
        response = f"针对查询: {original_query}\n\n"
        response += f"处理后的查询: {processed_query}\n\n"
        
        if time_info:
            response += "提取的时间信息:\n"
            for key, value in time_info.items():
                response += f"- {key}: {value}\n"
        else:
            response += "未提取到时间信息\n"
        
        return response
    
    async def reflect(self, result: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """反思执行结果，调整策略
        
        Args:
            result: 执行结果
            context: 上下文信息
            
        Returns:
            反思结果
        """
        logger.info(f"[TimeAgent] Reflecting on result")
        
        # 检查执行结果
        if 'final_response' in result:
            reflection = {
                'success': True,
                'response': result['final_response'],
                'confidence': 0.9 if 'error' not in result else 0.3,
                'suggestions': []
            }
            
            # 如果有错误，添加改进建议
            if 'error' in result:
                reflection['suggestions'].append('时间处理出现错误，建议检查查询语句')
                reflection['suggestions'].append('确保时间表达清晰明确')
        else:
            reflection = {
                'success': False,
                'error': '执行过程中出现错误',
                'suggestions': ['检查时间工具配置', '确认查询参数是否正确']
            }
        
        # 添加处理后的查询到反思结果，以便协调器重新分配任务
        if 'processed_query' in result:
            reflection['processed_query'] = result['processed_query']
        
        return reflection
