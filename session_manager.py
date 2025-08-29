"""
会话状态管理器 - 管理用户对话状态和多轮交互
"""
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import logging

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
        self.last_update = datetime.now()
    
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
    
    def __init__(self):
        self.sessions: Dict[str, SessionState] = {}
    
    def get_session(self, session_id: str) -> SessionState:
        """获取或创建会话"""
        if session_id not in self.sessions:
            self.sessions[session_id] = SessionState(session_id)
            logger.info(f"创建新会话: {session_id}")
        
        # 更新最后活动时间
        self.sessions[session_id].last_update = datetime.now()
        return self.sessions[session_id]
    
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
        now = datetime.now()
        expired_sessions = []
        
        for session_id, session in self.sessions.items():
            if (now - session.last_update).total_seconds() > hours * 3600:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            self.clear_session(session_id)
        
        if expired_sessions:
            logger.info(f"清理了 {len(expired_sessions)} 个过期会话")


# 全局会话管理器实例
session_manager = SessionManager()