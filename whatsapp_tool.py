"""
WhatsApp消息发送工具 - 基于AWS End User Messaging Social API
"""
from strands import tool
from typing import Optional
import os
import logging
import boto3
from botocore.exceptions import ClientError

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 尝试导入AWS SDK
try:
    import boto3
    from botocore.exceptions import ClientError
    AWS_SDK_AVAILABLE = True
except ImportError:
    AWS_SDK_AVAILABLE = False
    logger.warning("AWS SDK (boto3)未安装，WhatsApp消息发送功能不可用")

def send_whatsapp_message_tool(
    to_phone: str,
    message_body: str,
    origination_identity: Optional[str] = None,
    application_id: Optional[str] = None,
    message_type: str = "TRANSACTIONAL"
):
    """
    使用AWS End User Messaging Social发送WhatsApp消息
    
    Args:
        to_phone: 接收方手机号码 (格式: +1234567890)
        message_body: 消息内容
        origination_identity: 发起身份标识 (WhatsApp Business号码)
        application_id: AWS End User Messaging应用程序ID
        message_type: 消息类型 (TRANSACTIONAL 或 PROMOTIONAL)
    
    Returns:
        发送结果
    """
    if not AWS_SDK_AVAILABLE:
        return {"error": "AWS SDK (boto3)未安装，请先安装boto3库"}
    
    try:
        # 获取环境变量中的凭证
        origination_identity = origination_identity or os.getenv('WHATSAPP_ORIGINATION_IDENTITY')
        application_id = application_id or os.getenv('WHATSAPP_APPLICATION_ID')
        
        if not origination_identity:
            return {"error": "缺少发起身份标识，请提供origination_identity或设置WHATSAPP_ORIGINATION_IDENTITY环境变量"}
        
        if not application_id:
            return {"error": "缺少应用程序ID，请提供application_id或设置WHATSAPP_APPLICATION_ID环境变量"}
        
        # 初始化AWS End User Messaging客户端
        client = boto3.client('pinpoint-sms-voice-v2', region_name='us-east-1')
        
        # 发送WhatsApp消息
        response = client.send_text_message(
            DestinationPhoneNumber=f'whatsapp:{to_phone}',
            OriginationIdentity=origination_identity,
            MessageBody=message_body,
            MessageType=message_type,
            ConfigurationSetName=application_id
        )
        
        logger.info(f"WhatsApp消息发送成功: {response['MessageId']}")
        
        return {
            "status": "success",
            "message_id": response['MessageId'],
            "to": to_phone,
            "from": origination_identity,
            "body": message_body,
            "message_type": message_type
        }
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        logger.error(f"发送WhatsApp消息失败: {error_code} - {error_message}")
        return {"error": f"发送WhatsApp消息失败: {error_code} - {error_message}"}
    except Exception as e:
        logger.error(f"发送WhatsApp消息失败: {str(e)}")
        return {"error": f"发送WhatsApp消息失败: {str(e)}"}

# 使用装饰器注册为工具
@tool
def send_whatsapp_message(
    to_phone: str,
    message_body: str,
    origination_identity: Optional[str] = None,
    application_id: Optional[str] = None,
    message_type: str = "TRANSACTIONAL"
):
    """
    发送WhatsApp消息工具 (基于AWS End User Messaging Social)
    
    Args:
        to_phone: 接收方手机号码 (格式: +1234567890)
        message_body: 消息内容
        origination_identity: 发起身份标识 (WhatsApp Business号码)
        application_id: AWS End User Messaging应用程序ID
        message_type: 消息类型 (TRANSACTIONAL 或 PROMOTIONAL)
    
    Returns:
        发送结果
    """
    return send_whatsapp_message_tool(to_phone, message_body, origination_identity, application_id, message_type)
