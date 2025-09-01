"""
工具管理器 - 标准化工具注册和管理
"""
import logging
from typing import List, Dict, Any, Callable
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ToolInfo:
    """工具信息类"""
    
    def __init__(self, name: str, version: str, description: str, 
                 category: str, func: Callable, enabled: bool = True):
        self.name = name
        self.version = version
        self.description = description
        self.category = category
        self.func = func
        self.enabled = enabled
        self.registered_at = datetime.now()
        self.call_count = 0
        self.last_called = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "category": self.category,
            "enabled": self.enabled,
            "registered_at": self.registered_at.isoformat(),
            "call_count": self.call_count,
            "last_called": self.last_called.isoformat() if self.last_called else None
        }

class ToolManager:
    """工具管理器"""
    
    def __init__(self):
        self.tools: Dict[str, ToolInfo] = {}
        self.categories: Dict[str, List[str]] = {}
        logger.info("工具管理器初始化完成")
    
    def register_tool(self, name: str, version: str, description: str, 
                     category: str, func: Callable, enabled: bool = True) -> bool:
        """注册工具"""
        try:
            # 创建工具信息
            tool_info = ToolInfo(name, version, description, category, func, enabled)
            
            # 注册工具
            self.tools[name] = tool_info
            
            # 按类别分组
            if category not in self.categories:
                self.categories[category] = []
            self.categories[category].append(name)
            
            logger.info(f"工具已注册: {name} (版本: {version}, 类别: {category})")
            return True
        except Exception as e:
            logger.error(f"注册工具 {name} 失败: {e}")
            return False
    
    def get_tool(self, name: str) -> ToolInfo:
        """获取工具信息"""
        return self.tools.get(name)
    
    def get_tools_by_category(self, category: str) -> List[ToolInfo]:
        """按类别获取工具"""
        tool_names = self.categories.get(category, [])
        return [self.tools[name] for name in tool_names if name in self.tools]
    
    def get_all_tools(self) -> List[ToolInfo]:
        """获取所有工具"""
        return list(self.tools.values())
    
    def get_enabled_tools(self) -> List[ToolInfo]:
        """获取所有启用的工具"""
        return [tool for tool in self.tools.values() if tool.enabled]
    
    def enable_tool(self, name: str) -> bool:
        """启用工具"""
        if name in self.tools:
            self.tools[name].enabled = True
            logger.info(f"工具已启用: {name}")
            return True
        return False
    
    def disable_tool(self, name: str) -> bool:
        """禁用工具"""
        if name in self.tools:
            self.tools[name].enabled = False
            logger.info(f"工具已禁用: {name}")
            return True
        return False
    
    def get_tool_statistics(self) -> Dict[str, Any]:
        """获取工具统计信息"""
        total_tools = len(self.tools)
        enabled_tools = len([t for t in self.tools.values() if t.enabled])
        categories_count = len(self.categories)
        
        return {
            "total_tools": total_tools,
            "enabled_tools": enabled_tools,
            "disabled_tools": total_tools - enabled_tools,
            "categories": categories_count,
            "tools_by_category": {cat: len(tools) for cat, tools in self.categories.items()}
        }
    
    def call_tool(self, name: str, *args, **kwargs) -> Any:
        """调用工具并记录统计信息"""
        if name not in self.tools:
            raise ValueError(f"工具未找到: {name}")
        
        tool = self.tools[name]
        if not tool.enabled:
            raise ValueError(f"工具已禁用: {name}")
        
        try:
            # 调用工具函数
            result = tool.func(*args, **kwargs)
            
            # 更新统计信息
            tool.call_count += 1
            tool.last_called = datetime.now()
            
            logger.debug(f"工具调用成功: {name} (调用次数: {tool.call_count})")
            return result
        except Exception as e:
            logger.error(f"调用工具 {name} 失败: {e}")
            raise

# 全局工具管理器实例
tool_manager = ToolManager()