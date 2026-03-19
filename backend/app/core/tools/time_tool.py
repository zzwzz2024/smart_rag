"""
时间工具模块
用于解析用户查询中的相对时间表达式
"""
import re
from datetime import datetime, timedelta
from typing import Optional, Tuple

class TimeTool:
    """
    时间工具类，用于解析相对时间表达式
    """
    
    def __init__(self):
        """
        初始化时间工具
        """
        # 相对时间表达式的正则表达式
        self.time_patterns = {
            '去年': r'(去年|last year)',
            '前年': r'(前年|the year before last)',
            '今年': r'(今年|this year)',
            '明年': r'(明年|next year)',
            '后年': r'(后年|the year after next)',
            '上个月': r'(上个月|last month)',
            '这个月': r'(这个月|this month)',
            '下个月': r'(下个月|next month)',
            '上上个月': r'(上上个月|two months ago)',
            '下下个月': r'(下下个月|two months later)',
            '昨天': r'(昨天|yesterday)',
            '今天': r'(今天|today)',
            '明天': r'(明天|tomorrow)',
            '前天': r'(前天|the day before yesterday)',
            '后天': r'(后天|the day after tomorrow)',
            '上周': r'(上周|last week)',
            '本周': r'(本周|this week)',
            '下周': r'(下周|next week)',
            '上上周': r'(上上周|two weeks ago)',
            '下下周': r'(下下周|two weeks later)',
        }
    
    def parse_relative_time(self, query: str) -> Tuple[Optional[str], Optional[datetime]]:
        """
        解析查询中的相对时间表达式
        
        Args:
            query: 用户查询
            
        Returns:
            Tuple[Optional[str], Optional[datetime]]: (匹配的时间表达式, 解析后的时间)
        """
        now = datetime.now()
        
        for time_expr, pattern in self.time_patterns.items():
            if re.search(pattern, query):
                if time_expr == '去年' or time_expr == 'last year':
                    return time_expr, now.replace(year=now.year - 1)
                elif time_expr == '前年' or time_expr == 'the year before last':
                    return time_expr, now.replace(year=now.year - 2)
                elif time_expr == '今年' or time_expr == 'this year':
                    return time_expr, now
                elif time_expr == '明年' or time_expr == 'next year':
                    return time_expr, now.replace(year=now.year + 1)
                elif time_expr == '后年' or time_expr == 'the year after next':
                    return time_expr, now.replace(year=now.year + 2)
                elif time_expr == '上个月' or time_expr == 'last month':
                    if now.month == 1:
                        return time_expr, now.replace(year=now.year - 1, month=12)
                    else:
                        return time_expr, now.replace(month=now.month - 1)
                elif time_expr == '这个月' or time_expr == 'this month':
                    return time_expr, now
                elif time_expr == '下个月' or time_expr == 'next month':
                    if now.month == 12:
                        return time_expr, now.replace(year=now.year + 1, month=1)
                    else:
                        return time_expr, now.replace(month=now.month + 1)
                elif time_expr == '上上个月' or time_expr == 'two months ago':
                    if now.month <= 2:
                        return time_expr, now.replace(year=now.year - 1, month=now.month + 10)
                    else:
                        return time_expr, now.replace(month=now.month -