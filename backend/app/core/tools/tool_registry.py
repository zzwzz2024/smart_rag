"""工具注册表"""
from typing import Dict, Any


class ToolRegistry:
    """工具注册表"""
    
    def __init__(self):
        self.tools = {}
    
    def register_tool(self, tool_name: str, tool: Any):
        """注册工具
        
        Args:
            tool_name: 工具名称
            tool: 工具实例
        """
        self.tools[tool_name] = tool
    
    def get_tool(self, tool_name: str) -> Any:
        """获取工具
        
        Args:
            tool_name: 工具名称
            
        Returns:
            工具实例，如果不存在返回None
        """
        return self.tools.get(tool_name)
    
    def list_tools(self) -> list:
        """列出所有可用工具
        
        Returns:
            工具名称列表
        """
        return list(self.tools.keys())
