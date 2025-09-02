# WhatsApp消息发送工具使用说明

## 功能说明
WhatsApp消息发送工具允许通过AWS End User Messaging Social API发送WhatsApp消息。

## 安装依赖
```bash
pip install boto3
```

或者在requirements.txt中添加：
```
boto3
```

## 配置
要使用WhatsApp消息发送工具，您需要：

1. 在[AWS Pinpoint](https://aws.amazon.com/pinpoint/)中设置End User Messaging Social
2. 获取WhatsApp Business号码作为发起身份标识
3. 创建应用程序并获取应用程序ID

## AWS配置
确保您的AWS凭证已正确配置，可以通过以下方式之一：
1. AWS CLI配置 (`aws configure`)
2. 环境变量 (`AWS_ACCESS_KEY_ID` 和 `AWS_SECRET_ACCESS_KEY`)
3. IAM角色（如果在EC2或其他AWS服务上运行）

## 使用方法

### 1. 环境变量配置（推荐）
```bash
export WHATSAPP_ORIGINATION_IDENTITY=your_whatsapp_business_number
export WHATSAPP_APPLICATION_ID=your_application_id
```

### 2. 直接调用工具
```python
from whatsapp_tool import send_whatsapp_message

result = send_whatsapp_message(
    to_phone="+1234567890",  # 接收方电话号码
    message_body="Hello from WhatsApp!"  # 消息内容
)
```

### 3. 传递参数
```python
from whatsapp_tool import send_whatsapp_message

result = send_whatsapp_message(
    to_phone="+1234567890",
    message_body="Hello from WhatsApp!",
    origination_identity="your_whatsapp_business_number",
    application_id="your_application_id",
    message_type="TRANSACTIONAL"  # 或 "PROMOTIONAL"
)
```

## 参数说明
- `to_phone`: 接收方电话号码，格式为+1234567890
- `message_body`: 要发送的消息内容
- `origination_identity`: WhatsApp Business号码（发起身份标识）
- `application_id`: AWS Pinpoint应用程序ID
- `message_type`: 消息类型，可以是"TRANSACTIONAL"（事务性）或"PROMOTIONAL"（推广性）

## 返回值
成功时返回：
```json
{
    "status": "success",
    "message_id": "message-identifier",
    "to": "+1234567890",
    "from": "whatsapp-business-number",
    "body": "Hello from WhatsApp!",
    "message_type": "TRANSACTIONAL"
}
```

失败时返回：
```json
{
    "error": "错误信息"
}
```

## 错误处理
常见错误：
- 缺少凭证：确保AWS凭证已正确配置
- 缺少发起身份标识：确保提供了WhatsApp Business号码
- 缺少应用程序ID：确保提供了AWS Pinpoint应用程序ID
- 权限不足：确保AWS凭证具有Pinpoint SMS and Voice V2的适当权限
