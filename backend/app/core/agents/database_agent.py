"""数据库智能体"""
from typing import List, Dict, Any, Optional
from backend.app.core.agents.base_agent import BaseAgent
from loguru import logger


class DatabaseAgent(BaseAgent):
    """数据库智能体，专注于数据库查询和分析"""
    
    async def plan(self, task: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """规划任务执行步骤
        
        Args:
            task: 任务描述
            context: 上下文信息
            
        Returns:
            任务执行计划
        """
        logger.info(f"[DatabaseAgent] Planning task: {task}")
        
        # 生成执行计划
        plan = [
            {
                'step': 1,
                'action': 'analyze_query',
                'description': '分析查询意图，生成SQL',
                'params': {
                    'query': task
                }
            },
            {
                'step': 2,
                'action': 'execute_query',
                'description': '执行数据库查询',
                'params': {
                    'query': task
                }
            },
            {
                'step': 3,
                'action': 'format_response',
                'description': '格式化查询结果',
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
        logger.info(f"[DatabaseAgent] Executing plan with {len(plan)} steps")
        
        results = {}
        
        for step in plan:
            logger.info(f"[DatabaseAgent] Executing step {step['step']}: {step['description']}")
            
            if step['action'] == 'analyze_query':
                # 分析查询意图，生成SQL
                # 这里可以调用现有的SQL生成逻辑
                from backend.app.core.rag_pipeline import RAGPipeline
                if hasattr(self.rag_pipeline, '_detect_query_intent') and hasattr(self.rag_pipeline, '_generate_sql_query'):
                    intent = await self.rag_pipeline._detect_query_intent(
                        query=step['params']['query'],
                        model=context.get('model'),
                        api_key=context.get('api_key'),
                        base_url=context.get('base_url'),
                        model_id=context.get('model_id')
                    )
                    
                    if intent == 'database':
                        sql_query = await self.rag_pipeline._generate_sql_query(
                            query=step['params']['query'],
                            model=context.get('model'),
                            api_key=context.get('api_key'),
                            base_url=context.get('base_url'),
                            model_id=context.get('model_id')
                        )
                        results['sql_query'] = sql_query
                    else:
                        results['error'] = '非数据库查询意图'
                        return results
                else:
                    results['error'] = '缺少数据库查询能力'
                    return results
            
            elif step['action'] == 'execute_query':
                # 执行数据库查询
                if 'sql_query' in results:
                    try:
                        # 这里需要获取数据库会话
                        # 注意：实际实现中需要从上下文或其他方式获取数据库连接
                        # 暂时使用RAG pipeline的数据库连接逻辑
                        from backend.app.database import pm_async_session_factory
                        
                        # 创建数据库会话
                        async with pm_async_session_factory() as pm_db:
                            if hasattr(self.rag_pipeline, '_execute_sql_query'):
                                query_result = await self.rag_pipeline._execute_sql_query(
                                    results['sql_query'],
                                    pm_db
                                )
                                results['query_result'] = query_result
                            else:
                                results['error'] = '缺少SQL执行能力'
                    except Exception as e:
                        logger.error(f"Database query failed: {e}")
                        results['error'] = f'数据库查询失败: {str(e)}'
            
            elif step['action'] == 'format_response':
                # 格式化查询结果
                if 'query_result' in results:
                    # 使用RAG pipeline的生成器进行总结
                    if hasattr(self.rag_pipeline, 'generator'):
                        try:
                            # 构建上下文
                            context_str = "\n".join([str(row) for row in results['query_result']])
                            
                            # 构建消息
                            from backend.app.core.prompts import GENERATOR_PROMPT
                            messages = [
                                {"role": "system", "content": GENERATOR_PROMPT},
                                {"role": "user", "content": f"【参考信息】\n{context_str}\n\n【问题】\n{step['params']['query']}\n\n请根据参考信息回答问题，保持语言自然流畅，不要使用###标记，直接按点换行输出。"}
                            ]
                            
                            # 获取模型客户端
                            client = self.rag_pipeline.generator._get_or_create_client(
                                context.get('model_id'),
                                context.get('model'),
                                context.get('api_key'),
                                context.get('base_url')
                            )
                            
                            # 生成总结
                            response = await client.chat.completions.create(
                                model=context.get('model') or "",
                                messages=messages,
                                temperature=0.7,
                                max_tokens=1000
                            )
                            
                            results['final_response'] = response.choices[0].message.content
                        except Exception as e:
                            logger.error(f"LLM summarization failed: {e}")
                            # 失败时回退到原始格式化方法
                            results['final_response'] = self._format_query_result(results['query_result'])
                    else:
                        # 如果没有生成器，使用原始格式化方法
                        results['final_response'] = self._format_query_result(results['query_result'])
                else:
                    results['final_response'] = '数据库查询失败'
        
        return results
    
    def _format_query_result(self, query_result: List[Dict]) -> str:
        """格式化查询结果
        
        Args:
            query_result: 查询结果列表
            
        Returns:
            格式化后的字符串
        """
        if not query_result:
            return '未查询到数据'
        
        # 获取列名
        columns = list(query_result[0].keys())
        
        # 构建响应
        response = f"查询结果包含 {len(query_result)} 条记录，字段包括：{', '.join(columns)}\n\n"
        
        # 添加数据行
        for i, row in enumerate(query_result, 1):
            row_str = f"{i}. " + ', '.join([f"{col}: {val}" for col, val in row.items()])
            response += row_str + "\n"
        
        return response
    
    async def reflect(self, result: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """反思执行结果，调整策略
        
        Args:
            result: 执行结果
            context: 上下文信息
            
        Returns:
            反思结果
        """
        logger.info(f"[DatabaseAgent] Reflecting on result")
        
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
                reflection['suggestions'].append('数据库查询出现错误，建议检查查询语句')
                reflection['suggestions'].append('确保数据库连接正常')
        else:
            reflection = {
                'success': False,
                'error': '执行过程中出现错误',
                'suggestions': ['检查数据库连接', '确认查询参数是否正确']
            }
        
        return reflection
