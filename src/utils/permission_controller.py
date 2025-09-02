"""
权限控制器 - 管理应用权限和访问控制
"""
import os
import json
import logging
from typing import Dict, List, Optional, Set
from datetime import datetime
from enum import Enum

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Permission(Enum):
    """权限枚举"""
    READ_EMAILS = "read_emails"
    PROCESS_EMAILS = "process_emails"
    ACCESS_DATABASE = "access_database"
    MODIFY_DATA = "modify_data"
    ACCESS_FINANCIAL_DATA = "access_financial_data"
    ADMINISTER_SYSTEM = "administer_system"
    ACCESS_EXCHANGE_RATES = "access_exchange_rates"
    USE_LLM_ANALYSIS = "use_llm_analysis"

class Role(Enum):
    """角色枚举"""
    USER = "user"
    ADMIN = "admin"
    SYSTEM = "system"

class PermissionController:
    """权限控制器"""
    
    def __init__(self, config_file: str = "permissions.json"):
        self.config_file = config_file
        self.roles_permissions = self._load_permissions()
        logger.info("权限控制器初始化完成")
    
    def _load_permissions(self) -> Dict[str, List[str]]:
        """加载权限配置"""
        default_permissions = {
            Role.USER.value: [
                Permission.READ_EMAILS.value,
                Permission.PROCESS_EMAILS.value,
                Permission.ACCESS_DATABASE.value,
                Permission.ACCESS_FINANCIAL_DATA.value,
                Permission.ACCESS_EXCHANGE_RATES.value,
                Permission.USE_LLM_ANALYSIS.value
            ],
            Role.ADMIN.value: [
                Permission.READ_EMAILS.value,
                Permission.PROCESS_EMAILS.value,
                Permission.ACCESS_DATABASE.value,
                Permission.MODIFY_DATA.value,
                Permission.ACCESS_FINANCIAL_DATA.value,
                Permission.ADMINISTER_SYSTEM.value,
                Permission.ACCESS_EXCHANGE_RATES.value,
                Permission.USE_LLM_ANALYSIS.value
            ],
            Role.SYSTEM.value: [perm.value for perm in Permission]
        }
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    permissions = json.load(f)
                logger.info("权限配置已加载")
                return permissions
            else:
                # 保存默认权限配置
                self._save_permissions(default_permissions)
                logger.info("默认权限配置已创建")
                return default_permissions
        except Exception as e:
            logger.error(f"加载权限配置时出错，使用默认配置: {e}")
            return default_permissions
    
    def _save_permissions(self, permissions: Dict[str, List[str]]) -> bool:
        """保存权限配置"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(permissions, f, ensure_ascii=False, indent=2)
            logger.info("权限配置已保存")
            return True
        except Exception as e:
            logger.error(f"保存权限配置时出错: {e}")
            return False
    
    def get_role_permissions(self, role: str) -> Set[str]:
        """获取角色权限"""
        return set(self.roles_permissions.get(role, []))
    
    def has_permission(self, role: str, permission: str) -> bool:
        """检查角色是否具有特定权限"""
        permissions = self.get_role_permissions(role)
        return permission in permissions
    
    def has_any_permission(self, role: str, permissions: List[str]) -> bool:
        """检查角色是否具有任意一个权限"""
        role_permissions = self.get_role_permissions(role)
        return any(perm in role_permissions for perm in permissions)
    
    def has_all_permissions(self, role: str, permissions: List[str]) -> bool:
        """检查角色是否具有所有权限"""
        role_permissions = self.get_role_permissions(role)
        return all(perm in role_permissions for perm in permissions)
    
    def add_permission_to_role(self, role: str, permission: str) -> bool:
        """为角色添加权限"""
        if role not in self.roles_permissions:
            self.roles_permissions[role] = []
        
        if permission not in self.roles_permissions[role]:
            self.roles_permissions[role].append(permission)
            return self._save_permissions(self.roles_permissions)
        return True
    
    def remove_permission_from_role(self, role: str, permission: str) -> bool:
        """从角色移除权限"""
        if role in self.roles_permissions and permission in self.roles_permissions[role]:
            self.roles_permissions[role].remove(permission)
            return self._save_permissions(self.roles_permissions)
        return True
    
    def get_user_role(self, user_id: str) -> str:
        """获取用户角色（简化实现）"""
        # 在实际应用中，这里应该查询用户数据库或身份验证系统
        # 目前我们根据用户ID的前缀来确定角色
        if user_id.startswith("admin_"):
            return Role.ADMIN.value
        elif user_id.startswith("system_"):
            return Role.SYSTEM.value
        else:
            return Role.USER.value
    
    def check_user_permission(self, user_id: str, permission: str) -> bool:
        """检查用户是否具有特定权限"""
        role = self.get_user_role(user_id)
        return self.has_permission(role, permission)
    
    def get_all_permissions(self) -> List[str]:
        """获取所有权限"""
        all_permissions = set()
        for perms in self.roles_permissions.values():
            all_permissions.update(perms)
        return list(all_permissions)

# 全局权限控制器实例
permission_controller = PermissionController()