"""
会话状态管理器 - 管理用户对话状态和多轮交互
"""
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json
import logging
import pickle
import os

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SessionState:
    """会话状态类"""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.current_state = "idle"  # idle, processing, review, confirming, completed
        self.current_email_account = None
        self.processed_emails: List[Dict] = []
        self.modified_data: Dict[str, Any] = {}
        self.confirmation_status: Dict[str, bool] = {}
        self.modification_history: List[Dict] = []
        self.created_at = datetime.now()
        self.last_update = datetime.now()
    
    def update_last_activity(self):
        """更新最后活动时间"""
        self.last_update = datetime.now()
    
    def is_expired(self, timeout_hours: int = 24) -> bool:
        """检查会话是否过期"""
        return (datetime.now() - self.last_update) > timedelta(hours=timeout_hours)
    
    def save_to_file(self, directory: str = "sessions") -> bool:
        """将会话保存到文件"""
        try:
            # 确保目录存在
            os.makedirs(directory, exist_ok=True)
            
            # 保存会话数据
            file_path = os.path.join(directory, f"session_{self.session_id}.pkl")
            with open(file_path, 'wb') as f:
                pickle.dump(self.__dict__, f)
            
            logger.info(f"会话 {self.session_id} 已保存到 {file_path}")
            return True
        except Exception as e:
            logger.error(f"保存会话 {self.session_id} 失败: {e}")
            return False
    
    @classmethod
    def load_from_file(cls, session_id: str, directory: str = "sessions") -> Optional['SessionState']:
        """从文件加载会话"""
        try:
            file_path = os.path.join(directory, f"session_{session_id}.pkl")
            if not os.path.exists(file_path):
                return None
            
            with open(file_path, 'rb') as f:
                data = pickle.load(f)
            
            # 创建新的会话实例并恢复数据
            session = cls(session_id)
            session.__dict__.update(data)
            
            # 检查是否过期
            if session.is_expired():
                logger.info(f"会话 {session_id} 已过期，删除文件")
                os.remove(file_path)
                return None
            
            logger.info(f"会话 {session_id} 从 {file_path} 加载成功")
            return session
        except Exception as e:
            logger.error(f"加载会话 {session_id} 失败: {e}")
            return None
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "session_id": self.session_id,
            "current_state": self.current_state,
            "current_email_account": self.current_email_account,
            "processed_emails_count": len(self.processed_emails),
            "modified_data_count": len(self.modified_data),
            "confirmation_status": self.confirmation_status,
            "modification_history_count": len(self.modification_history),
            "last_update": self.last_update.isoformat()
        }


class SessionManager:
    """会话管理器"""
    
    def __init__(self, session_directory: str = "sessions"):
        self.sessions: Dict[str, SessionState] = {}
        self.session_directory = session_directory
        # 确保会话目录存在
        os.makedirs(session_directory, exist_ok=True)
    
    def get_session(self, session_id: str) -> SessionState:
        """获取或创建会话"""
        # 首先检查内存中是否存在
        if session_id not in self.sessions:
            # 尝试从文件加载
            session = SessionState.load_from_file(session_id, self.session_directory)
            if session is not None:
                self.sessions[session_id] = session
                logger.info(f"从文件加载会话: {session_id}")
            else:
                # 创建新会话
                self.sessions[session_id] = SessionState(session_id)
                logger.info(f"创建新会话: {session_id}")
        
        # 更新最后活动时间
        self.sessions[session_id].update_last_activity()
        return self.sessions[session_id]
    
    def save_session(self, session_id: str) -> bool:
        """保存会话到文件"""
        if session_id in self.sessions:
            return self.sessions[session_id].save_to_file(self.session_directory)
        return False
    
    def save_all_sessions(self) -> None:
        """保存所有会话到文件"""
        saved_count = 0
        for session_id in list(self.sessions.keys()):
            if self.save_session(session_id):
                saved_count += 1
        logger.info(f"保存了 {saved_count} 个会话到文件")
    
    def update_session_state(self, session_id: str, state: str) -> None:
        """更新会话状态"""
        session = self.get_session(session_id)
        session.current_state = state
        logger.info(f"会话 {session_id} 状态更新为: {state}")
    
    def set_email_account(self, session_id: str, email_account: str) -> None:
        """设置当前邮箱账户"""
        session = self.get_session(session_id)
        session.current_email_account = email_account
        logger.info(f"会话 {session_id} 设置邮箱账户: {email_account}")
    
    def store_processed_emails(self, session_id: str, emails: List[Dict]) -> None:
        """存储处理的邮件数据"""
        session = self.get_session(session_id)
        session.processed_emails = emails
        logger.info(f"会话 {session_id} 存储了 {len(emails)} 封邮件数据")
    
    def add_modification(self, session_id: str, email_id: str, field: str, 
                        old_value: Any, new_value: Any, reason: str = "") -> None:
        """添加修改记录"""
        session = self.get_session(session_id)
        
        # 存储修改数据
        if email_id not in session.modified_data:
            session.modified_data[email_id] = {}
        session.modified_data[email_id][field] = new_value
        
        # 记录修改历史
        modification = {
            "timestamp": datetime.now().isoformat(),
            "email_id": email_id,
            "field": field,
            "old_value": old_value,
            "new_value": new_value,
            "reason": reason
        }
        session.modification_history.append(modification)
        
        logger.info(f"会话 {session_id} 邮件 {email_id} 字段 {field} 修改: {old_value} -> {new_value}")
    
    def set_confirmation(self, session_id: str, email_id: str, confirmed: bool) -> None:
        """设置确认状态"""
        session = self.get_session(session_id)
        session.confirmation_status[email_id] = confirmed
        status = "确认" if confirmed else "拒绝"
        logger.info(f"会话 {session_id} 邮件 {email_id} {status}")
    
    def get_session_summary(self, session_id: str) -> Dict:
        """获取会话摘要"""
        session = self.get_session(session_id)
        return session.to_dict()
    
    def clear_session(self, session_id: str) -> None:
        """清空会话"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info(f"清空会话: {session_id}")
    
    def cleanup_old_sessions(self, hours: int = 24) -> None:
        """清理过期会话"""
        # 保存所有会话到文件
        self.save_all_sessions()
        
        # 清理内存中的过期会话
        now = datetime.now()
        expired_sessions = []
        
        for session_id, session in self.sessions.items():
            if (now - session.last_update).total_seconds() > hours * 3600:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            self.clear_session(session_id)
        
        # 清理磁盘上的过期会话文件
        cleaned_files = 0
        try:
            if os.path.exists(self.session_directory):
                for filename in os.listdir(self.session_directory):
                    if filename.startswith("session_") and filename.endswith(".pkl"):
                        file_path = os.path.join(self.session_directory, filename)
                        # 检查文件修改时间
                        file_modified = datetime.fromtimestamp(os.path.getmtime(file_path))
                        if (now - file_modified).total_seconds() > hours * 3600:
                            os.remove(file_path)
                            cleaned_files += 1
        except Exception as e:
            logger.error(f"清理过期会话文件时出错: {e}")
        
        if expired_sessions or cleaned_files:
            logger.info(f"清理了 {len(expired_sessions)} 个内存会话和 {cleaned_files} 个磁盘文件")


# 全局会话管理器实例
session_manager = SessionManager()