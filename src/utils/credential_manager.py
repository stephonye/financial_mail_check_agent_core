"""
安全凭证管理器 - 管理和保护应用凭证
"""
import os
import json
import logging
from typing import Optional, Dict, Any
from cryptography.fernet import Fernet
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CredentialManager:
    """凭证管理器"""
    
    def __init__(self, key_file: str = "secret.key", credentials_file: str = "credentials.json"):
        self.key_file = key_file
        self.credentials_file = credentials_file
        self.key = self._load_or_generate_key()
        self.cipher = Fernet(self.key)
        self.credentials = self._load_credentials()
        logger.info("凭证管理器初始化完成")
    
    def _load_or_generate_key(self) -> bytes:
        """加载或生成加密密钥"""
        try:
            if os.path.exists(self.key_file):
                with open(self.key_file, 'rb') as key_file:
                    key = key_file.read()
                logger.info("加密密钥已加载")
            else:
                # 生成新的密钥
                key = Fernet.generate_key()
                with open(self.key_file, 'wb') as key_file:
                    key_file.write(key)
                # 设置文件权限为仅所有者可读写
                os.chmod(self.key_file, 0o600)
                logger.info("新的加密密钥已生成并保存")
            return key
        except Exception as e:
            logger.error(f"处理加密密钥时出错: {e}")
            raise
    
    def _load_credentials(self) -> Dict[str, Any]:
        """加载凭证"""
        try:
            if os.path.exists(self.credentials_file):
                with open(self.credentials_file, 'rb') as cred_file:
                    encrypted_data = cred_file.read()
                
                # 解密数据
                decrypted_data = self.cipher.decrypt(encrypted_data)
                credentials = json.loads(decrypted_data.decode('utf-8'))
                logger.info("凭证已加载并解密")
                return credentials
            else:
                logger.info("凭证文件不存在，将创建新的凭证存储")
                return {}
        except Exception as e:
            logger.error(f"加载凭证时出错: {e}")
            return {}
    
    def _save_credentials(self) -> bool:
        """保存凭证"""
        try:
            # 加密数据
            credentials_json = json.dumps(self.credentials, ensure_ascii=False)
            encrypted_data = self.cipher.encrypt(credentials_json.encode('utf-8'))
            
            # 保存到文件
            with open(self.credentials_file, 'wb') as cred_file:
                cred_file.write(encrypted_data)
            
            # 设置文件权限为仅所有者可读写
            os.chmod(self.credentials_file, 0o600)
            logger.info("凭证已加密并保存")
            return True
        except Exception as e:
            logger.error(f"保存凭证时出错: {e}")
            return False
    
    def store_credential(self, key: str, value: str, description: str = "") -> bool:
        """存储凭证"""
        try:
            self.credentials[key] = {
                "value": value,
                "description": description,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            # 保存凭证
            if self._save_credentials():
                logger.info(f"凭证已存储: {key}")
                return True
            else:
                logger.error(f"存储凭证失败: {key}")
                return False
        except Exception as e:
            logger.error(f"存储凭证 {key} 时出错: {e}")
            return False
    
    def get_credential(self, key: str) -> Optional[str]:
        """获取凭证"""
        credential_info = self.credentials.get(key)
        if credential_info:
            return credential_info.get("value")
        return None
    
    def update_credential(self, key: str, value: str, description: str = "") -> bool:
        """更新凭证"""
        if key in self.credentials:
            self.credentials[key]["value"] = value
            self.credentials[key]["description"] = description
            self.credentials[key]["updated_at"] = datetime.now().isoformat()
            
            # 保存凭证
            if self._save_credentials():
                logger.info(f"凭证已更新: {key}")
                return True
            else:
                logger.error(f"更新凭证失败: {key}")
                return False
        else:
            logger.warning(f"凭证不存在: {key}")
            return False
    
    def delete_credential(self, key: str) -> bool:
        """删除凭证"""
        if key in self.credentials:
            del self.credentials[key]
            
            # 保存凭证
            if self._save_credentials():
                logger.info(f"凭证已删除: {key}")
                return True
            else:
                logger.error(f"删除凭证后保存失败: {key}")
                return False
        else:
            logger.warning(f"凭证不存在: {key}")
            return False
    
    def list_credentials(self) -> Dict[str, Dict[str, Any]]:
        """列出所有凭证（不包含实际值）"""
        result = {}
        for key, info in self.credentials.items():
            result[key] = {
                "description": info.get("description", ""),
                "created_at": info.get("created_at", ""),
                "updated_at": info.get("updated_at", "")
            }
        return result
    
    def get_credential_info(self, key: str) -> Optional[Dict[str, Any]]:
        """获取凭证信息（不包含实际值）"""
        credential_info = self.credentials.get(key)
        if credential_info:
            return {
                "description": credential_info.get("description", ""),
                "created_at": credential_info.get("created_at", ""),
                "updated_at": credential_info.get("updated_at", "")
            }
        return None

# 全局凭证管理器实例
credential_manager = CredentialManager()