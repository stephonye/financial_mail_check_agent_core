"""
Gmail邮件处理器 - 支持多账户和对话式验证的财务邮件处理
"""
import os
import json
import re
import base64
from datetime import datetime
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup

# Google API imports
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# 新增导入
from exchange_service import ExchangeRateService
from database_service import DatabaseService
from session_manager import session_manager
from llm_email_analyzer import LLMEmailAnalyzer, analyze_email_content_llm
import os

# Gmail API 配置
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

class EmailProcessor:
    def __init__(self, credentials_path: str = 'credentials.json', token_path: str = 'token.json', 
                 email_account: str = None):
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.email_account = email_account
        self.service = None
        self.exchange_service = ExchangeRateService()
        
        # 检查是否启用MCP连接
        use_mcp = os.getenv('MCP_ENABLED', 'false').lower() == 'true'
        self.db_service = DatabaseService(use_mcp=use_mcp)
        
        # 初始化LLM分析器
        self.llm_analyzer = LLMEmailAnalyzer()
    
    def authenticate_gmail_for_account(self, email_account: str = None) -> bool:
        """为特定邮箱账户认证Gmail API"""
        if email_account:
            self.email_account = email_account
        
        # 为不同账户使用不同的token文件
        account_suffix = f"_{self.email_account.replace('@', '_').replace('.', '_')}" if self.email_account else ""
        token_file = f"token{account_suffix}.json"
        
        try:
            creds = None
            
            if os.path.exists(token_file):
                creds = Credentials.from_authorized_user_file(token_file, SCOPES)
            
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_path, SCOPES)
                    
                    # 设置登录提示，要求用户选择账户
                    creds = flow.run_local_server(
                        port=0,
                        prompt='select_account' if self.email_account else 'consent'
                    )
                
                with open(token_file, 'w') as token:
                    token.write(creds.to_json())
            
            self.service = build('gmail', 'v1', credentials=creds)
            
            if self.email_account:
                logger.info(f"成功认证邮箱账户: {self.email_account}")
            else:
                logger.info("成功认证Gmail API")
            
            return True
            
        except Exception as e:
            logger.error(f"Gmail认证失败: {e}")
            return False
    
    def authenticate_gmail(self):
        """认证Gmail API（向后兼容）"""
        return self.authenticate_gmail_for_account()
    
    def search_emails(self, query: str, max_results: int = 50) -> List[Dict]:
        """搜索邮件"""
        try:
            results = self.service.users().messages().list(
                userId='me', q=query, maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            email_details = []
            
            for message in messages:
                msg = self.service.users().messages().get(
                    userId='me', id=message['id'], format='full'
                ).execute()
                
                email_info = self._parse_email(msg)
                if email_info:
                    email_details.append(email_info)
            
            return email_details
            
        except HttpError as error:
            print(f'An error occurred: {error}')
            return []
    
    def _parse_email(self, msg: Dict) -> Optional[Dict]:
        """解析邮件内容"""
        try:
            # 获取邮件头部信息
            headers = msg['payload']['headers']
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '')
            from_email = next((h['value'] for h in headers if h['name'] == 'From'), '')
            date = next((h['value'] for h in headers if h['name'] == 'Date'), '')
            
            # 获取邮件正文
            body = self._get_email_body(msg['payload'])
            
            # 解析财务信息
            financial_info = self._extract_financial_info(subject, body)
            
            if financial_info:
                return {
                    'id': msg['id'],
                    'subject': subject,
                    'from': from_email,
                    'date': date,
                    'body_preview': body[:200] + '...' if len(body) > 200 else body,
                    'financial_info': financial_info
                }
            
            return None
            
        except Exception as e:
            print(f'Error parsing email: {e}')
            return None
    
    def _get_email_body(self, payload: Dict) -> str:
        """提取邮件正文"""
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    data = part['body']['data']
                    return base64.urlsafe_b64decode(data).decode('utf-8')
                elif part['mimeType'] == 'text/html':
                    data = part['body']['data']
                    html_content = base64.urlsafe_b64decode(data).decode('utf-8')
                    soup = BeautifulSoup(html_content, 'lxml')
                    return soup.get_text()
        
        # 如果没有parts，直接获取body
        if 'body' in payload and 'data' in payload['body']:
            data = payload['body']['data']
            return base64.urlsafe_b64decode(data).decode('utf-8')
        
        return ''
    
    def _extract_financial_info(self, subject: str, body: str) -> Optional[Dict]:
        """提取财务信息 - 使用LLM增强分析"""
        # 检查是否为财务相关邮件
        financial_keywords = ['invoice', 'order', 'statement', 'payment', 'bill', 'receipt']
        subject_lower = subject.lower()
        
        if not any(keyword in subject_lower for keyword in financial_keywords):
            return None
        
        # 首先使用LLM进行智能分析
        llm_result = self._analyze_with_llm(subject, body)
        
        # 如果LLM分析成功且置信度高，优先使用LLM结果
        if llm_result.get('confidence', 0) > 0.7:
            return self._format_llm_result(llm_result, subject)
        
        # 否则使用规则分析作为回退
        return self._extract_with_rules(subject, body)
    
    def _analyze_with_llm(self, subject: str, body: str) -> Dict:
        """使用LLM分析邮件内容"""
        try:
            # 推断邮件类型用于更好的LLM提示
            email_type = self._identify_document_type(subject)
            
            # 使用LLM分析
            llm_result = self.llm_analyzer.analyze_email_with_llm(subject, body, email_type)
            
            # 补充汇率转换信息
            if llm_result.get('amount') and llm_result.get('currency'):
                amount = llm_result['amount']
                currency = llm_result['currency']
                
                if currency and currency.upper() != 'USD':
                    usd_amount = self.exchange_service.convert_amount(amount, currency, 'USD')
                    if usd_amount:
                        llm_result['usd_amount'] = float(usd_amount)
                        llm_result['exchange_rate'] = float(usd_amount) / float(amount)
                elif currency and currency.upper() == 'USD':
                    llm_result['usd_amount'] = amount
                    llm_result['exchange_rate'] = 1.0
            
            return llm_result
            
        except Exception as e:
            print(f"LLM分析失败，使用规则分析: {e}")
            return {'confidence': 0, 'analysis_method': 'rule_based_fallback'}
    
    def _format_llm_result(self, llm_result: Dict, subject: str) -> Dict:
        """格式化LLM分析结果"""
        return {
            'type': llm_result.get('document_type'),
            'status': llm_result.get('status'),
            'counterparty': llm_result.get('counterparty'),
            'amount': llm_result.get('amount'),
            'currency': llm_result.get('currency'),
            'usd_amount': llm_result.get('usd_amount'),
            'exchange_rate': llm_result.get('exchange_rate'),
            'dates': {
                'issue_date': llm_result.get('issue_date'),
                'due_date': llm_result.get('due_date')
            },
            'subject': subject,
            'llm_analysis': {
                'confidence': llm_result.get('confidence'),
                'anomalies': llm_result.get('anomalies', []),
                'extracted_entities': llm_result.get('extracted_entities', []),
                'description': llm_result.get('description', ''),
                'analysis_method': llm_result.get('analysis_method', 'llm')
            }
        }
    
    def _extract_with_rules(self, subject: str, body: str) -> Optional[Dict]:
        """使用规则提取财务信息（回退方法）"""
        # 提取金额和币种
        amount, currency = self._extract_amount_and_currency(body)
        
        # 汇率转换
        usd_amount = None
        exchange_rate = None
        
        if amount and currency and currency.upper() != 'USD':
            usd_amount = self.exchange_service.convert_amount(amount, currency, 'USD')
            if usd_amount:
                exchange_rate = float(usd_amount) / float(amount)
        elif amount and currency and currency.upper() == 'USD':
            usd_amount = amount
            exchange_rate = 1.0
        
        # 识别状态
        status = self._identify_status(body)
        
        # 提取对手信息
        counterparty = self._extract_counterparty(subject, body)
        
        # 提取日期信息
        dates = self._extract_dates(body)
        
        if any([amount, status, counterparty, dates]):
            return {
                'type': self._identify_document_type(subject),
                'status': status,
                'counterparty': counterparty,
                'amount': amount,
                'currency': currency,
                'usd_amount': float(usd_amount) if usd_amount else None,
                'exchange_rate': exchange_rate,
                'dates': dates,
                'subject': subject,
                'llm_analysis': {
                    'confidence': 0.3,
                    'anomalies': [],
                    'extracted_entities': [],
                    'description': '',
                    'analysis_method': 'rule_based'
                }
            }
        
        return None
    
    def _identify_document_type(self, subject: str) -> str:
        """识别文档类型"""
        subject_lower = subject.lower()
        
        if 'invoice' in subject_lower:
            return 'invoice'
        elif 'order' in subject_lower:
            return 'order'
        elif 'statement' in subject_lower:
            return 'statement'
        else:
            return 'other'
    
    def _identify_status(self, body: str) -> str:
        """识别付款状态"""
        body_lower = body.lower()
        
        if any(phrase in body_lower for phrase in ['payment received', 'paid in full', 'payment completed']):
            return '完成付款'
        elif any(phrase in body_lower for phrase in ['payment due', 'please pay', 'amount due']):
            return '收款'
        elif any(phrase in body_lower for phrase in ['make payment', 'pay now', 'payment required']):
            return '付款'
        else:
            return '其他'
    
    def _extract_counterparty(self, subject: str, body: str) -> str:
        """提取对手信息"""
        # 从主题中提取公司名
        company_patterns = [
            r'from\s+([A-Za-z\s&]+)',
            r'by\s+([A-Za-z\s&]+)',
            r'@([A-Za-z0-9]+)',
            r'([A-Z][a-z]+\s+[A-Z][a-z]+)'  # 公司名通常有大写字母
        ]
        
        for pattern in company_patterns:
            match = re.search(pattern, subject, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        # 从正文中提取
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        email_match = re.search(email_pattern, body)
        if email_match:
            return email_match.group(0)
        
        return 'Unknown'
    
    def _extract_amount_and_currency(self, body: str) -> tuple:
        """提取金额和币种"""
        # 金额模式
        amount_patterns = [
            r'\$\s*([0-9,]+(?:\.[0-9]{2})?)',  # USD
            r'USD\s*([0-9,]+(?:\.[0-9]{2})?)',
            r'€\s*([0-9,]+(?:\.[0-9]{2})?)',   # EUR
            r'EUR\s*([0-9,]+(?:\.[0-9]{2})?)',
            r'¥\s*([0-9,]+(?:\.[0-9]{2})?)',   # JPY/CNY
            r'CNY\s*([0-9,]+(?:\.[0-9]{2})?)',
            r'amount:\s*([0-9,]+(?:\.[0-9]{2})?)',
            r'total:\s*([0-9,]+(?:\.[0-9]{2})?)'
        ]
        
        currency_symbols = {
            '$': 'USD',
            'USD': 'USD',
            '€': 'EUR', 
            'EUR': 'EUR',
            '¥': 'CNY',
            'CNY': 'CNY'
        }
        
        for pattern in amount_patterns:
            match = re.search(pattern, body, re.IGNORECASE)
            if match:
                amount = match.group(1).replace(',', '')
                # 确定币种
                currency = 'USD'  # 默认
                for symbol, curr in currency_symbols.items():
                    if symbol in pattern:
                        currency = curr
                        break
                return float(amount), currency
        
        return None, None
    
    def _extract_dates(self, body: str) -> Dict:
        """提取日期信息"""
        dates = {}
        
        # 日期模式
        date_patterns = {
            'due_date': [r'due date[:\s]*([0-9]{1,2}/[0-9]{1,2}/[0-9]{4})',
                        r'due[:\s]*([A-Za-z]+\s+[0-9]{1,2},?\s+[0-9]{4})'],
            'issue_date': [r'date[:\s]*([0-9]{1,2}/[0-9]{1,2}/[0-9]{4})',
                          r'issued[:\s]*([A-Za-z]+\s+[0-9]{1,2},?\s+[0-9]{4})'],
            'start_date': [r'start[:\s]*([0-9]{1,2}/[0-9]{1,2}/[0-9]{4})',
                          r'from[:\s]*([A-Za-z]+\s+[0-9]{1,2},?\s+[0-9]{4})']
        }
        
        for date_type, patterns in date_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, body, re.IGNORECASE)
                if match:
                    dates[date_type] = match.group(1)
                    break
        
        return dates
    
    def save_to_json(self, data: List[Dict], filename: str = 'financial_emails.json'):
        """保存数据到JSON文件"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return filename
    
    def save_to_database(self, data: List[Dict]) -> int:
        """保存数据到PostgreSQL数据库"""
        success_count = 0
        for email_data in data:
            if self.db_service.insert_financial_email(email_data):
                success_count += 1
        
        return success_count
    
    def save_confirmed_data(self, session_id: str) -> Dict:
        """保存已确认的数据到数据库"""
        session = session_manager.get_session(session_id)
        
        confirmed_emails = []
        for email in session.processed_emails:
            email_id = email.get('id')
            
            # 只保存已确认的邮件
            if session.confirmation_status.get(email_id, False):
                # 应用修改
                if email_id in session.modified_data:
                    financial_info = email.get('financial_info', {})
                    for field, value in session.modified_data[email_id].items():
                        if field in financial_info:
                            financial_info[field] = value
                
                confirmed_emails.append(email)
        
        if confirmed_emails:
            success_count = self.save_to_database(confirmed_emails)
            return {
                "status": "success",
                "saved_count": success_count,
                "total_confirmed": len(confirmed_emails),
                "message": f"成功保存 {success_count} 条已确认的记录"
            }
        else:
            return {
                "status": "no_data",
                "message": "没有已确认的数据需要保存"
            }


def process_financial_emails(save_to_db: bool = True) -> Dict:
    """处理财务邮件的主函数"""
    processor = EmailProcessor()
    
    # 搜索财务相关邮件
    query = 'subject:(invoice OR order OR statement)'
    financial_emails = processor.search_emails(query)
    
    # 获取连接类型信息
    connection_type = "MCP" if processor.db_service.use_mcp else "直接"
    
    result = {
        'total_emails_found': len(financial_emails),
        'emails': financial_emails,
        'json_file': None,
        'db_success_count': 0,
        'connection_type': connection_type
    }
    
    # 保存结果
    if financial_emails:
        # 保存到JSON文件
        output_file = processor.save_to_json(financial_emails)
        result['json_file'] = output_file
        
        # 保存到数据库
        if save_to_db:
            db_success_count = processor.save_to_database(financial_emails)
            result['db_success_count'] = db_success_count
            
            print(f"找到 {len(financial_emails)} 封财务邮件。JSON保存到 {output_file}，通过{connection_type}连接成功插入 {db_success_count} 条记录到数据库")
        else:
            print(f"找到 {len(financial_emails)} 封财务邮件。保存到 {output_file}")
    else:
        print("未找到财务邮件。")
    
    return result


def process_emails_with_session(session_id: str, email_account: str = None, query: str = None) -> Dict:
    """
    对话式处理邮件 - 支持会话管理和多账户
    
    Args:
        session_id: 会话ID
        email_account: 邮箱账户地址
        query: 搜索查询条件
    
    Returns:
        处理结果和会话状态
    """
    # 更新会话状态
    session_manager.update_session_state(session_id, "processing")
    
    if email_account:
        session_manager.set_email_account(session_id, email_account)
    
    # 创建处理器并认证
    processor = EmailProcessor(email_account=email_account)
    
    if not processor.authenticate_gmail_for_account(email_account):
        session_manager.update_session_state(session_id, "error")
        return {
            "status": "error",
            "message": "Gmail认证失败，请检查账户权限"
        }
    
    # 搜索邮件
    search_query = query or 'subject:(invoice OR order OR statement)'
    financial_emails = processor.search_emails(search_query)
    
    if not financial_emails:
        session_manager.update_session_state(session_id, "completed")
        return {
            "status": "no_emails",
            "message": "未找到符合条件的财务邮件",
            "session_state": session_manager.get_session_summary(session_id)
        }
    
    # 存储到会话
    session_manager.store_processed_emails(session_id, financial_emails)
    session_manager.update_session_state(session_id, "review")
    
    # 准备审核数据
    review_data = []
    for email in financial_emails[:5]:  # 只显示前5封用于审核
        financial_info = email.get('financial_info', {})
        review_data.append({
            "email_id": email['id'],
            "subject": email['subject'],
            "from": email['from'],
            "date": email['date'],
            "amount": financial_info.get('amount'),
            "currency": financial_info.get('currency'),
            "usd_amount": financial_info.get('usd_amount'),
            "status": financial_info.get('status'),
            "type": financial_info.get('type')
        })
    
    return {
        "status": "success",
        "total_emails": len(financial_emails),
        "review_data": review_data,
        "message": f"找到 {len(financial_emails)} 封财务邮件，请审核以下数据",
        "session_state": session_manager.get_session_summary(session_id),
        "next_step": "请确认数据是否正确，或提出修改要求"
    }


def confirm_and_save_session(session_id: str) -> Dict:
    """确认并保存会话中的数据"""
    session = session_manager.get_session(session_id)
    
    if not session.processed_emails:
        return {
            "status": "error",
            "message": "会话中没有可保存的数据"
        }
    
    # 创建处理器
    processor = EmailProcessor()
    
    # 保存已确认的数据
    save_result = processor.save_confirmed_data(session_id)
    
    if save_result["status"] == "success":
        session_manager.update_session_state(session_id, "completed")
        
        # 获取统计信息
        confirmed_count = sum(1 for status in session.confirmation_status.values() if status)
        modified_count = len(session.modified_data)
        
        save_result["session_summary"] = {
            "total_emails": len(session.processed_emails),
            "confirmed_count": confirmed_count,
            "modified_count": modified_count,
            "modification_history_count": len(session.modification_history)
        }
    
    return save_result


if __name__ == "__main__":
    result = process_financial_emails()
    
    # 显示统计信息
    if result['emails']:
        print("\n=== 处理结果统计 ===")
        print(f"总邮件数: {result['total_emails_found']}")
        print(f"JSON文件: {result['json_file']}")
        print(f"数据库成功记录: {result['db_success_count']}")
        
        # 显示汇率转换统计
        currencies = {}
        total_original = 0
        total_usd = 0
        
        for email in result['emails']:
            financial_info = email.get('financial_info', {})
            currency = financial_info.get('currency')
            amount = financial_info.get('amount')
            usd_amount = financial_info.get('usd_amount')
            
            if currency and amount:
                currencies[currency] = currencies.get(currency, 0) + 1
                total_original += amount
            if usd_amount:
                total_usd += usd_amount
        
        print(f"涉及币种: {', '.join(currencies.keys())}")
        print(f"原始金额总计: {total_original:.2f}")
        print(f"USD金额总计: {total_usd:.2f}")