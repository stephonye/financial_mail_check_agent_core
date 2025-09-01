'''
Descripttion: ****
version: 1.0.0
Author: Stephon Ye
Date: 2025-08-028 22:49:16
LastEditors: Stephon Ye
LastEditTime: 2025-08-29 13:06:04
'''
from strands import Agent, tool
from strands_tools import calculator, current_time
from strands.models.bedrock import BedrockModel

# Import the AgentCore SDK
from bedrock_agentcore.runtime import BedrockAgentCoreApp

# Import email processing functionality
try:
    from email_processor import EmailProcessor, process_financial_emails
    from database_service import DatabaseService
except ImportError:
    # Fallback for testing without email dependencies
    EmailProcessor = None
    process_financial_emails = None
    DatabaseService = None

WELCOME_MESSAGE = """
Welcome to the Customer Support Assistant! How can I help you today?
"""

SYSTEM_PROMPT = """
You are an helpful customer support assistant.
When provided with a customer email, gather all necessary info and prepare the response email.
When asked about an order, look for it and tell the full description and date of the order to the customer.
Don't mention the customer ID in your reply.
"""


@tool
def get_customer_id(email_address: str):
    if email_address == "me@example.net":
        return {"customer_id": 123}
    else:
        return {"message": "customer not found"}


@tool
def get_orders(customer_id: int):
    if customer_id == 123:
        return [{
            "order_id": 1234,
            "items": ["smartphone", "smartphone USB-C charger", "smartphone black cover"],
            "date": "20250607"
        }]
    else:
        return {"message": "no order found"}


@tool
def get_knowledge_base_info(topic: str):
    kb_info = []
    if "smartphone" in topic:
        if "cover" in topic:
            kb_info.append("To put on the cover, insert the bottom first, then push from the back up to the top.")
            kb_info.append("To remove the cover, push the top and bottom of the cover at the same time.")
        if "charger" in topic:
            kb_info.append("Input: 100-240V AC, 50/60Hz")
            kb_info.append("Includes US/UK/EU plug adapters")
    if len(kb_info) > 0:
        return kb_info
    else:
        return {"message": "no info found"}


@tool
def process_financial_emails_tool(max_results: int = 20):
    """
    搜索和处理Gmail中的财务邮件（发票、订单、对账单）
    
    Args:
        max_results: 最大返回结果数量
    
    Returns:
        包含财务信息的JSON数据
    """
    if EmailProcessor is None:
        return {"error": "Email processing dependencies not available. Please install required packages."}
    
    try:
        processor = EmailProcessor()
        
        # 搜索财务相关邮件
        query = 'subject:(invoice OR order OR statement)'
        financial_emails = processor.search_emails(query, max_results)
        
        if financial_emails:
            # 保存到JSON文件
            output_file = processor.save_to_json(financial_emails)
            
            return {
                "status": "success",
                "count": len(financial_emails),
                "output_file": output_file,
                "emails": financial_emails
            }
        else:
            return {"status": "no_emails_found", "message": "No financial emails found matching the criteria."}
            
    except Exception as e:
        return {"error": f"Failed to process emails: {str(e)}"}


@tool  
def get_financial_email_summary():
    """
    获取财务邮件的统计摘要信息
    
    Returns:
        财务邮件统计信息
    """
    if DatabaseService is not None:
        # 使用数据库获取统计信息
        try:
            db_service = DatabaseService()
            stats = db_service.get_summary_stats()
            
            # 获取最近几条记录作为示例
            recent_emails = db_service.get_financial_emails(5)
            
            return {
                "status": "success",
                "source": "database",
                "summary": stats,
                "recent_emails": recent_emails
            }
            
        except Exception as e:
            return {"error": f"Database query failed: {str(e)}"}
    
    elif EmailProcessor is not None:
        # 回退到邮件搜索方式
        try:
            processor = EmailProcessor()
            
            # 搜索所有财务邮件
            query = 'subject:(invoice OR order OR statement)'
            financial_emails = processor.search_emails(query, 100)
            
            if not financial_emails:
                return {"status": "no_emails_found"}
            
            # 统计信息
            summary = {
                "total_emails": len(financial_emails),
                "by_type": {},
                "by_status": {},
                "total_amount": 0,
                "currencies": {}
            }
            
            for email in financial_emails:
                financial_info = email.get('financial_info', {})
                
                # 按类型统计
                doc_type = financial_info.get('type', 'unknown')
                summary['by_type'][doc_type] = summary['by_type'].get(doc_type, 0) + 1
                
                # 按状态统计
                status = financial_info.get('status', 'unknown')
                summary['by_status'][status] = summary['by_status'].get(status, 0) + 1
                
                # 金额统计
                amount = financial_info.get('amount')
                currency = financial_info.get('currency')
                if amount and currency:
                    summary['total_amount'] += amount
                    summary['currencies'][currency] = summary['currencies'].get(currency, 0) + amount
            
            return {
                "status": "success",
                "source": "email_search",
                "summary": summary,
                "sample_emails": financial_emails[:3]  # 返回前3个邮件作为示例
            }
            
        except Exception as e:
            return {"error": f"Failed to generate summary: {str(e)}"}
    else:
        return {"error": "Email processing dependencies not available."}


@tool
def query_financial_emails(limit: int = 10, document_type: str = None, status: str = None):
    """
    查询数据库中的财务邮件记录
    
    Args:
        limit: 返回记录数量
        document_type: 文档类型过滤 (invoice/order/statement)
        status: 状态过滤 (收款/付款/完成付款/其他)
    
    Returns:
        财务邮件查询结果
    """
    if DatabaseService is None:
        return {"error": "Database service not available."}
    
    try:
        db_service = DatabaseService()
        
        # 构建查询条件
        where_conditions = []
        params = []
        
        if document_type:
            where_conditions.append("document_type = %s")
            params.append(document_type)
        
        if status:
            where_conditions.append("status = %s")
            params.append(status)
        
        # 构建SQL查询
        query = "SELECT * FROM financial_emails"
        if where_conditions:
            query += " WHERE " + " AND ".join(where_conditions)
        
        query += " ORDER BY processed_at DESC LIMIT %s"
        params.append(limit)
        
        with db_service.conn.cursor() as cur:
            cur.execute(query, params)
            results = cur.fetchall()
            
            # 转换为字典列表
            columns = [desc[0] for desc in cur.description]
            emails = [dict(zip(columns, row)) for row in results]
            
            return {
                "status": "success",
                "count": len(emails),
                "emails": emails
            }
            
    except Exception as e:
        return {"error": f"Database query failed: {str(e)}"}


# Create an AgentCore app
app = BedrockAgentCoreApp()

# Use Amazon Nova Pro model - supports system messages and direct invocation
model = BedrockModel(model_id="amazon.nova-pro-v1:0")

# 创建工具列表
agent_tools = [calculator, current_time, get_customer_id, get_orders, get_knowledge_base_info]

# 如果邮件处理功能可用，添加邮件处理工具
if EmailProcessor is not None:
    agent_tools.extend([process_financial_emails_tool, get_financial_email_summary])

# 如果数据库服务可用，添加数据库查询工具
if DatabaseService is not None:
    agent_tools.append(query_financial_emails)

agent = Agent(
    model=model,
    system_prompt=SYSTEM_PROMPT,
    tools=agent_tools
)


# Specify the entry point function invoking the agent
@app.entrypoint
def invoke(payload):
    """Handler for agent invocation"""
    user_message = payload.get(
        "prompt", "No prompt found in input, please guide customer to create a json payload with prompt key"
    )
    result = agent(user_message)
    return {"result": result.message}


if __name__ == "__main__":
    app.run()
