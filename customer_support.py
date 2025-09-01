"""
Financial Email Processor - AWS AgentCore based Gmail财务数据处理
version: 1.0.0
Author: Stephon Ye
Date: 2025-08-29
Description: AWS AgentCore财务邮件处理Agent，支持Gmail邮件处理和数据分析
"""
from strands import Agent, tool
from strands_tools import calculator, current_time
from strands.models.bedrock import BedrockModel
from strands_tools.agent_core_memory import AgentCoreMemoryToolProvider
from datetime import datetime
from tool_manager import tool_manager
from typing import Dict, List, Optional, Any

# Import the AgentCore SDK
from bedrock_agentcore.runtime import BedrockAgentCoreApp

# Import email processing functionality
try:
    from email_processor import EmailProcessor, process_financial_emails, process_emails_with_session, confirm_and_save_session
    from database_service import DatabaseService
    from session_manager import session_manager
    from llm_email_analyzer import analyze_email_content_llm
except ImportError:
    # Fallback for testing without email dependencies
    EmailProcessor = None
    process_financial_emails = None
    process_emails_with_session = None
    confirm_and_save_session = None
    DatabaseService = None
    session_manager = None
    analyze_email_content_llm = None

WELCOME_MESSAGE = """
Welcome to the Financial Email Processor! 
I can help you process and analyze financial emails from Gmail.

I can assist with:
- Searching and processing financial emails (invoices, orders, statements)
- Extracting financial information with currency conversion
- Storing data in PostgreSQL database (direct or via MCP)
- Providing statistical analysis of financial data
- General conversation and calculations
"""

SYSTEM_PROMPT = """
You are a financial email processing assistant built on AWS AgentCore.
You specialize in analyzing and processing financial documents from Gmail emails
while maintaining conversational capabilities.

Your capabilities include:
1. Searching for and processing financial emails (invoices, orders, statements)
2. Extracting financial information including amounts, currencies, dates
3. Converting foreign currencies to USD using real-time exchange rates
4. Storing processed data in PostgreSQL database (direct or MCP connection)
5. Providing statistical analysis and queries on financial data
6. General conversation and assistance using standard tools
7. Memory management for ongoing conversations

Maintain a helpful and professional tone. When processing financial emails,
provide clear summaries and insights. For database operations, indicate whether
you're using direct connection or MCP protocol.
"""


@tool
def get_customer_id(email_address: str):
    """根据邮箱地址获取客户ID（基础对话功能）"""
    if email_address == "me@example.net":
        return {"customer_id": 123}
    else:
        return {"message": "customer not found"}


@tool
def get_orders(customer_id: int):
    """查询客户订单信息（基础对话功能）"""
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
    """获取知识库信息（基础对话功能）"""
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
def process_financial_emails_tool(max_results: int = 20, user_id: str = "default_user"):
    """
    搜索和处理Gmail中的财务邮件（发票、订单、对账单）
    
    Args:
        max_results: 最大返回结果数量
        user_id: 用户ID，用于权限控制
    
    Returns:
        包含财务信息的处理结果
    """
    if EmailProcessor is None:
        return {"error": "Email processing dependencies not available. Please install required packages."}
    
    try:
        processor = EmailProcessor(user_id=user_id)
        
        # 搜索财务相关邮件
        query = 'subject:(invoice OR order OR statement)'
        financial_emails = processor.search_emails(query, max_results)
        
        if financial_emails:
            # 保存到JSON文件
            output_file = processor.save_to_json(financial_emails)
            
            # 保存到数据库
            db_success_count = processor.save_to_database(financial_emails)
            
            return {
                "status": "success",
                "count": len(financial_emails),
                "db_success_count": db_success_count,
                "output_file": output_file,
                "message": f"Processed {len(financial_emails)} emails, {db_success_count} saved to database"
            }
        else:
            return {"status": "no_emails_found", "message": "No financial emails found matching the criteria."}
            
    except Exception as e:
        return {"error": f"Failed to process emails: {str(e)}"}


@tool  
def get_financial_email_summary(user_id: str = "default_user"):
    """
    获取财务邮件的统计摘要信息
    
    Args:
        user_id: 用户ID，用于权限控制
    
    Returns:
        财务邮件统计信息
    """
    if DatabaseService is not None:
        # 使用数据库获取统计信息
        try:
            db_service = DatabaseService(user_id=user_id)
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
            processor = EmailProcessor(user_id=user_id)
            
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
                "sample_emails": financial_emails[:3]
            }
            
        except Exception as e:
            return {"error": f"Failed to generate summary: {str(e)}"}
    else:
        return {"error": "Email processing dependencies not available."}


@tool
def query_financial_emails(limit: int = 10, document_type: str = None, status: str = None, user_id: str = "default_user"):
    """
    查询数据库中的财务邮件记录
    
    Args:
        limit: 返回记录数量
        document_type: 文档类型过滤 (invoice/order/statement)
        status: 状态过滤 (收款/付款/完成付款/其他)
        user_id: 用户ID，用于权限控制
    
    Returns:
        财务邮件查询结果
    """
    if DatabaseService is None:
        return {"error": "Database service not available."}
    
    try:
        db_service = DatabaseService(user_id=user_id)
        
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
        
        emails = db_service.get_financial_emails(limit)
        
        return {
            "status": "success",
            "count": len(emails),
            "emails": emails
        }
            
    except Exception as e:
        return {"error": f"Database query failed: {str(e)}"}


@tool
def process_emails_interactive(session_id: str, email_account: str = None, query: str = None, user_id: str = "default_user"):
    """
    对话式处理财务邮件 - 支持多账户和用户交互
    
    Args:
        session_id: 会话ID（用于多轮对话）
        email_account: 要处理的邮箱账户地址
        query: 自定义搜索查询条件
        user_id: 用户ID，用于权限控制
    
    Returns:
        处理结果和审核数据
    """
    if process_emails_with_session is None:
        return {"error": "Email processing with session not available."}
    
    try:
        # 传递用户ID到处理函数
        result = process_emails_with_session(session_id, email_account, query, user_id)
        return result
        
    except Exception as e:
        return {"error": f"Interactive email processing failed: {str(e)}"}


@tool  
def confirm_email_data(session_id: str, email_id: str, confirmed: bool = True, 
                      modifications: Optional[Dict[str, Any]] = None):
    """
    确认或修改邮件数据
    
    Args:
        session_id: 会话ID
        email_id: 邮件ID
        confirmed: 是否确认数据
        modifications: 修改内容 {字段: 新值}
    
    Returns:
        确认结果
    """
    if session_manager is None:
        return {"error": "Session management not available."}
    
    try:
        # 设置确认状态
        session_manager.set_confirmation(session_id, email_id, confirmed)
        
        # 处理修改
        if modifications:
            session = session_manager.get_session(session_id)
            # 找到对应的邮件数据
            for email in session.processed_emails:
                if email.get('id') == email_id:
                    financial_info = email.get('financial_info', {})
                    for field, new_value in modifications.items():
                        if field in financial_info:
                            old_value = financial_info[field]
                            session_manager.add_modification(
                                session_id, email_id, field, old_value, new_value,
                                f"用户修改: {old_value} -> {new_value}"
                            )
        
        return {
            "status": "success",
            "email_id": email_id,
            "confirmed": confirmed,
            "modifications_applied": modifications is not None,
            "session_state": session_manager.get_session_summary(session_id)
        }
        
    except Exception as e:
        return {"error": f"Confirmation failed: {str(e)}"}


@tool
def save_confirmed_data(session_id: str, user_id: str = "default_user"):
    """
    保存已确认的数据到数据库
    
    Args:
        session_id: 会话ID
        user_id: 用户ID，用于权限控制
    
    Returns:
        保存结果
    """
    if confirm_and_save_session is None:
        return {"error": "Save functionality not available."}
    
    try:
        result = confirm_and_save_session(session_id, user_id)
        return result
        
    except Exception as e:
        return {"error": f"Save operation failed: {str(e)}"}


@tool
def get_session_status(session_id: str):
    """
    获取会话状态信息
    
    Args:
        session_id: 会话ID
    
    Returns:
        会话状态摘要
    """
    if session_manager is None:
        return {"error": "Session management not available."}
    
    try:
        summary = session_manager.get_session_summary(session_id)
        return {
            "status": "success",
            "session_summary": summary
        }
        
    except Exception as e:
        return {"error": f"Failed to get session status: {str(e)}"}


@tool
def analyze_email_with_llm(subject: str, body: str, email_type: str = None):
    """
    使用LLM深度分析邮件内容，提取结构化财务信息
    
    Args:
        subject: 邮件主题
        body: 邮件正文内容
        email_type: 邮件类型 (invoice/order/statement/payment/receipt/other)
    
    Returns:
        包含详细财务信息的分析结果
    """
    if analyze_email_content_llm is None:
        return {"error": "LLM邮件分析功能不可用，请检查依赖包安装"}
    
    try:
        # 使用LLM分析邮件内容
        analysis_result = analyze_email_content_llm(subject, body, email_type)
        
        return {
            "status": "success",
            "analysis_method": analysis_result.get('analysis_method', 'llm'),
            "confidence": analysis_result.get('confidence', 0.5),
            "financial_info": {
                "document_type": analysis_result.get('document_type'),
                "status": analysis_result.get('status'),
                "counterparty": analysis_result.get('counterparty'),
                "amount": analysis_result.get('amount'),
                "currency": analysis_result.get('currency'),
                "usd_amount": analysis_result.get('usd_amount'),
                "exchange_rate": analysis_result.get('exchange_rate'),
                "issue_date": analysis_result.get('issue_date'),
                "due_date": analysis_result.get('due_date')
            },
            "analysis_metadata": {
                "anomalies": analysis_result.get('anomalies', []),
                "extracted_entities": analysis_result.get('extracted_entities', []),
                "description": analysis_result.get('description', '')
            },
            "recommendations": _generate_recommendations(analysis_result)
        }
        
    except Exception as e:
        return {"error": f"LLM邮件分析失败: {str(e)}"}


def _generate_recommendations(analysis_result: Dict) -> List[str]:
    """基于分析结果生成建议"""
    recommendations = []
    
    # 检查异常
    anomalies = analysis_result.get('anomalies', [])
    if anomalies:
        recommendations.append(f"发现{len(anomalies)}个异常点，建议仔细核查")
    
    # 检查置信度
    confidence = analysis_result.get('confidence', 0)
    if confidence < 0.5:
        recommendations.append("分析置信度较低，建议人工复核")
    
    # 检查金额
    amount = analysis_result.get('amount')
    if amount and amount > 10000:
        recommendations.append("大额交易，建议双重确认")
    
    # 检查币种
    currency = analysis_result.get('currency')
    if currency and currency != 'USD':
        recommendations.append(f"外币交易({currency})，注意汇率波动风险")
    
    return recommendations if recommendations else ["分析结果正常，可继续处理"]


# Create an AgentCore app
app = BedrockAgentCoreApp()

# Use Amazon Nova Pro model - supports system messages and direct invocation
model = BedrockModel(model_id="amazon.nova-pro-v1:0")

# 注册基础工具
tool_manager.register_tool("calculator", "1.0.0", "基本计算器功能", "基础工具", calculator)
tool_manager.register_tool("current_time", "1.0.0", "获取当前时间", "基础工具", current_time)
tool_manager.register_tool("get_customer_id", "1.0.0", "根据邮箱地址获取客户ID", "客户工具", get_customer_id)
tool_manager.register_tool("get_orders", "1.0.0", "查询客户订单信息", "订单工具", get_orders)
tool_manager.register_tool("get_knowledge_base_info", "1.0.0", "获取知识库信息", "知识库工具", get_knowledge_base_info)

# 如果邮件处理功能可用，注册邮件处理工具
if EmailProcessor is not None:
    tool_manager.register_tool("process_financial_emails", "1.0.0", "搜索和处理Gmail中的财务邮件", "邮件工具", process_financial_emails_tool)
    tool_manager.register_tool("get_financial_email_summary", "1.0.0", "获取财务邮件的统计摘要信息", "邮件工具", get_financial_email_summary)

# 如果数据库服务可用，注册数据库查询工具
if DatabaseService is not None:
    tool_manager.register_tool("query_financial_emails", "1.0.0", "查询数据库中的财务邮件记录", "数据库工具", query_financial_emails)

# 注册对话式邮件处理工具
if all([process_emails_with_session, confirm_and_save_session, session_manager]):
    tool_manager.register_tool("process_emails_interactive", "1.0.0", "对话式处理财务邮件", "邮件工具", process_emails_interactive)
    tool_manager.register_tool("confirm_email_data", "1.0.0", "确认或修改邮件数据", "邮件工具", confirm_email_data)
    tool_manager.register_tool("save_confirmed_data", "1.0.0", "保存已确认的数据到数据库", "数据库工具", save_confirmed_data)
    tool_manager.register_tool("get_session_status", "1.0.0", "获取会话状态信息", "会话工具", get_session_status)

# 注册LLM邮件分析工具
if analyze_email_content_llm is not None:
    tool_manager.register_tool("analyze_email_with_llm", "1.0.0", "使用LLM深度分析邮件内容", "AI工具", analyze_email_with_llm)

# 注册AgentCore内存管理工具
memory_tool_provider = AgentCoreMemoryToolProvider()
for memory_tool in memory_tool_provider.tools:
    tool_manager.register_tool(
        memory_tool.__name__ if hasattr(memory_tool, '__name__') else str(memory_tool),
        "1.0.0",
        "AgentCore内存管理工具",
        "内存工具",
        memory_tool
    )

# 获取所有启用的工具
agent_tools = [tool_info.func for tool_info in tool_manager.get_enabled_tools()]

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
        "prompt", "No prompt found in input, please provide a prompt for financial email processing"
    )
    result = agent(user_message)
    return {"result": result.message}


# Health check endpoint
@app.route("/health")
def health_check():
    """Health check endpoint for AWS Bedrock AgentCore"""
    # 检查数据库连接状态
    db_status = "unknown"
    if DatabaseService is not None:
        try:
            db_service = DatabaseService()
            if db_service.connect():
                db_status = "connected"
                db_service.disconnect()
            else:
                db_status = "disconnected"
        except:
            db_status = "error"
    
    # 检查ExchangeRateService状态
    exchange_service_status = "unknown"
    try:
        from exchange_service import ExchangeRateService
        exchange_service = ExchangeRateService()
        if exchange_service.get_exchange_rate("USD", "USD") == 1.0:
            exchange_service_status = "operational"
        else:
            exchange_service_status = "degraded"
    except:
        exchange_service_status = "error"
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "financial-email-processor",
        "version": "1.0.0",
        "components": {
            "database": db_status,
            "exchange_service": exchange_service_status,
            "email_processor": "available" if EmailProcessor is not None else "unavailable"
        }
    }


# Readiness check endpoint
@app.route("/ready")
def readiness_check():
    """Readiness check endpoint"""
    # 检查必要的依赖和服务
    dependencies_ready = True
    
    if EmailProcessor is None:
        dependencies_ready = False
    
    return {
        "status": "ready" if dependencies_ready else "not_ready",
        "dependencies": {
            "email_processor": EmailProcessor is not None,
            "database_service": DatabaseService is not None,
            "session_manager": session_manager is not None
        }
    }


if __name__ == "__main__":
    app.run()