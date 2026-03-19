"""
时间工具模块
用于处理时间相关的查询，如去年、前年、上个月、下个月等
"""
from datetime import datetime, timedelta
import re


def get_time_relative_to_now(relative_time: str) -> str:
    """
    根据相对时间获取具体的时间
    
    Args:
        relative_time: 相对时间，如"去年"、"前年"、"上个月"、"下个月"等
        
    Returns:
        str: 具体的时间字符串
    """
    now = datetime.now()
    
    if "去年" in relative_time:
        last_year = now.year - 1
        return f"{last_year}年"
    elif "前年" in relative_time:
        two_years_ago = now.year - 2
        return f"{two_years_ago}年"
    elif "今年" in relative_time:
        return f"{now.year}年"
    elif "上个月" in relative_time:
        last_month = now - timedelta(days=30)
        return f"{last_month.year}年{last_month.month}月"
    elif "下个月" in relative_time:
        next_month = now + timedelta(days=30)
        return f"{next_month.year}年{next_month.month}月"
    elif "上周" in relative_time:
        last_week = now - timedelta(weeks=1)
        return f"{last_week.year}年{last_week.month}月{last_week.day}日"
    elif "下周" in relative_time:
        next_week = now + timedelta(weeks=1)
        return f"{next_week.year}年{next_week.month}月{next_week.day}日"
    elif "昨天" in relative_time:
        yesterday = now - timedelta(days=1)
        return f"{yesterday.year}年{yesterday.month}月{yesterday.day}日"
    elif "今天" in relative_time:
        return f"{now.year}年{now.month}月{now.day}日"
    elif "明天" in relative_time:
        tomorrow = now + timedelta(days=1)
        return f"{tomorrow.year}年{tomorrow.month}月{tomorrow.day}日"
    else:
        return relative_time


def replace_relative_time_in_query(query: str) -> str:
    """
    替换查询中的相对时间为具体时间
    
    Args:
        query: 用户查询
        
    Returns:
        str: 替换后的查询
    """
    # 匹配常见的相对时间表达式
    relative_time_patterns = [
        "去年", "前年", "今年",
        "上个月", "下个月",
        "上周", "下周",
        "昨天", "今天", "明天"
    ]
    
    for pattern in relative_time_patterns:
        if pattern in query:
            specific_time = get_time_relative_to_now(pattern)
            query = query.replace(pattern, specific_time)
    
    return query


def extract_time_from_query(query: str) -> str:
    """
    从查询中提取时间信息
    
    Args:
        query: 用户查询
        
    Returns:
        str: 提取的时间信息
    """
    # 匹配具体的时间格式，如"2023年12月"、"2024年"等
    time_pattern = r"\d{4}年(\d{1,2}月)?(\d{1,2}日)?"
    matches = re.findall(time_pattern, query)
    
    if matches:
        return matches[0][0] if matches[0][0] else matches[0]
    
    # 如果没有具体时间，检查是否有相对时间
    relative_time_patterns = [
        "去年", "前年", "今年",
        "上个月", "下个月",
        "上周", "下周",
        "昨天", "今天", "明天"
    ]
    
    for pattern in relative_time_patterns:
        if pattern in query:
            return get_time_relative_to_now(pattern)
    
    return ""
