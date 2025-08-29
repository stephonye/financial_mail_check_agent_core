"""
LLM邮件分析器 - 使用Amazon Bedrock LLM增强邮件内容分析
"""
import json
import re
from typing import Dict, Any, Optional, List
from strands import Agent

class LLMEmailAnalyzer:
    def __init__(self, model_id: str = "amazon.nova-pro-v1:0"):
        """初始化LLM邮件分析器"""
        self.agent = Agent(model=model_id)
        
    def analyze_email_with_llm(self, subject: str, body: str, email_type: str = None) -> Dict:
        """
        使用LLM分析邮件内容，提取结构化财务信息
        
        Args:
            subject: 邮件主题
            body: 邮件正文
            email_type: 邮件类型（invoice/order/statement等）
            
        Returns:
            结构化的财务信息
        """
        # 构建LLM提示词
        prompt = self._build_analysis_prompt(subject, body, email_type)
        
        try:
            # 调用LLM进行分析
            response = self.agent(prompt)
            
            # 解析LLM响应
            analysis_result = self._parse_llm_response(response.message)
            
            # 验证和清理结果
            validated_result = self._validate_analysis_result(analysis_result, subject, body)
            
            return validated_result
            
        except Exception as e:
            print(f"LLM分析失败: {e}")
            # 失败时回退到规则分析
            return self._fallback_rule_based_analysis(subject, body)
    
    def _build_analysis_prompt(self, subject: str, body: str, email_type: str = None) -> str:
        """构建LLM分析提示词"""
        email_type_context = f"This appears to be a {email_type} email." if email_type else ""
        
        prompt = f"""
你是一个专业的财务邮件分析专家。请分析以下邮件内容，提取结构化财务信息。

邮件主题: {subject}

邮件正文:
{body[:2000]}  # 限制正文长度

{email_type_context}

请提取以下信息并以JSON格式返回：
1. document_type: 文档类型 (invoice, order, statement, payment, receipt, other)
2. status: 状态 (收款, 付款, 完成付款, 待处理, 其他)
3. counterparty: 交易对手方名称
4. amount: 金额 (数字)
5. currency: 币种 (USD, EUR, CNY, JPY, GBP, 或其他)
6. usd_amount: 转换为USD的金额 (如适用)
7. exchange_rate: 汇率 (如适用)
8. issue_date: 签发日期 (YYYY-MM-DD格式)
9. due_date: 到期日期 (YYYY-MM-DD格式)
10. description: 交易描述摘要
11. confidence: 分析置信度 (0-1)
12. anomalies: 异常或可疑点列表
13. extracted_entities: 提取的关键实体列表

对于不确定的信息，请使用null或合理推断。

请只返回JSON格式的结果，不要包含其他文本。
"""
        return prompt.strip()
    
    def _parse_llm_response(self, response: str) -> Dict:
        """解析LLM响应，提取JSON数据"""
        try:
            # 尝试从响应中提取JSON
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                return json.loads(json_str)
            else:
                # 如果没有找到JSON，尝试解析为键值对
                return self._parse_key_value_response(response)
        except json.JSONDecodeError:
            print("LLM响应JSON解析失败")
            return {}
    
    def _parse_key_value_response(self, response: str) -> Dict:
        """解析键值对格式的响应"""
        result = {}
        lines = response.split('\n')
        
        for line in lines:
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip().lower().replace(' ', '_')
                value = value.strip()
                
                # 转换数字和布尔值
                if value.lower() in ['true', 'false']:
                    result[key] = value.lower() == 'true'
                elif value.replace('.', '').isdigit():
                    result[key] = float(value) if '.' in value else int(value)
                elif value == 'null' or value == 'None':
                    result[key] = None
                else:
                    result[key] = value
        
        return result
    
    def _validate_analysis_result(self, result: Dict, subject: str, body: str) -> Dict:
        """验证和清理LLM分析结果"""
        validated = {
            'document_type': result.get('document_type'),
            'status': result.get('status', '其他'),
            'counterparty': result.get('counterparty'),
            'amount': self._validate_number(result.get('amount')),
            'currency': self._validate_currency(result.get('currency')),
            'usd_amount': self._validate_number(result.get('usd_amount')),
            'exchange_rate': self._validate_number(result.get('exchange_rate')),
            'issue_date': result.get('issue_date'),
            'due_date': result.get('due_date'),
            'description': result.get('description', ''),
            'confidence': min(max(float(result.get('confidence', 0.5)), 0), 1),
            'anomalies': result.get('anomalies', []),
            'extracted_entities': result.get('extracted_entities', []),
            'analysis_method': 'llm',
            'raw_llm_response': result
        }
        
        # 补充缺失信息
        if not validated['document_type']:
            validated['document_type'] = self._infer_document_type(subject)
        
        if not validated['counterparty']:
            validated['counterparty'] = self._extract_counterparty_from_subject(subject)
        
        return validated
    
    def _validate_number(self, value) -> Optional[float]:
        """验证数字值"""
        if value is None:
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None
    
    def _validate_currency(self, currency: str) -> Optional[str]:
        """验证币种"""
        if not currency:
            return None
        
        currency = currency.upper().strip()
        valid_currencies = ['USD', 'EUR', 'CNY', 'JPY', 'GBP', 'AUD', 'CAD', 'CHF']
        
        if currency in valid_currencies:
            return currency
        else:
            # 尝试映射常见符号
            currency_map = {
                '$': 'USD',
                '€': 'EUR',
                '¥': 'JPY',
                '£': 'GBP',
                '\u00a3': 'GBP'  # £的Unicode
            }
            return currency_map.get(currency, None)
    
    def _infer_document_type(self, subject: str) -> str:
        """从主题推断文档类型"""
        subject_lower = subject.lower()
        
        if any(word in subject_lower for word in ['invoice', '发票']):
            return 'invoice'
        elif any(word in subject_lower for word in ['order', '订单']):
            return 'order'
        elif any(word in subject_lower for word in ['statement', '对账单']):
            return 'statement'
        elif any(word in subject_lower for word in ['payment', '付款']):
            return 'payment'
        elif any(word in subject_lower for word in ['receipt', '收据']):
            return 'receipt'
        else:
            return 'other'
    
    def _extract_counterparty_from_subject(self, subject: str) -> str:
        """从主题提取对手方"""
        # 简单规则提取
        patterns = [
            r'from\s+([A-Za-z\s&]+)',
            r'by\s+([A-Za-z\s&]+)',
            r'@([A-Za-z0-9]+)',
            r'([A-Z][a-z]+\s+[A-Z][a-z]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, subject, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return 'Unknown'
    
    def _fallback_rule_based_analysis(self, subject: str, body: str) -> Dict:
        """LLM失败时的回退规则分析"""
        # 避免循环导入，使用本地导入
        try:
            from email_processor import EmailProcessor
            
            # 使用原有的规则分析
            processor = EmailProcessor()
            
            # 提取基础信息
            amount, currency = processor._extract_amount_and_currency(body)
            status = processor._identify_status(body)
            counterparty = processor._extract_counterparty(subject, body)
            doc_type = processor._identify_document_type(subject)
            
            return {
                'document_type': doc_type,
                'status': status,
                'counterparty': counterparty,
                'amount': amount,
                'currency': currency,
                'usd_amount': None,
                'exchange_rate': None,
                'issue_date': None,
                'due_date': None,
                'description': f"{doc_type} from {counterparty}",
                'confidence': 0.3,  # 规则分析置信度较低
                'anomalies': [],
                'extracted_entities': [],
                'analysis_method': 'rule_based',
                'raw_llm_response': None
            }
            
        except ImportError:
            # 回退到简单规则分析
            return self._simple_rule_based_analysis(subject, body)
    
    def _simple_rule_based_analysis(self, subject: str, body: str) -> Dict:
        """简单规则分析（无EmailProcessor依赖）"""
        # 基础规则分析
        subject_lower = subject.lower()
        
        # 识别文档类型
        if 'invoice' in subject_lower:
            doc_type = 'invoice'
        elif 'order' in subject_lower:
            doc_type = 'order'
        elif 'statement' in subject_lower:
            doc_type = 'statement'
        else:
            doc_type = 'other'
        
        # 简单金额提取
        amount_match = re.search(r'\$\s*([0-9,]+(?:\.[0-9]{2})?)', body)
        amount = float(amount_match.group(1).replace(',', '')) if amount_match else None
        
        return {
            'document_type': doc_type,
            'status': '其他',
            'counterparty': 'Unknown',
            'amount': amount,
            'currency': 'USD' if amount else None,
            'usd_amount': amount,
            'exchange_rate': 1.0 if amount else None,
            'issue_date': None,
            'due_date': None,
            'description': f"{doc_type}",
            'confidence': 0.2,  # 简单分析置信度更低
            'anomalies': [],
            'extracted_entities': [],
            'analysis_method': 'simple_rule_based',
            'raw_llm_response': None
        }
    
    def detect_anomalies(self, financial_info: Dict) -> List[str]:
        """检测财务信息中的异常"""
        anomalies = []
        
        # 检查金额异常
        amount = financial_info.get('amount')
        if amount and amount > 1000000:  # 超过100万
            anomalies.append(f"大额交易: ${amount:,.2f}")
        
        # 检查币种不一致
        currency = financial_info.get('currency')
        subject = financial_info.get('subject', '')
        if currency and subject:
            if currency == 'USD' and '$' not in subject:
                anomalies.append("币种与主题符号不一致")
            elif currency == 'EUR' and '€' not in subject:
                anomalies.append("币种与主题符号不一致")
        
        # 检查日期合理性
        due_date = financial_info.get('due_date')
        issue_date = financial_info.get('issue_date')
        if due_date and issue_date:
            # 这里可以添加更复杂的日期验证逻辑
            pass
        
        return anomalies


def analyze_email_content_llm(subject: str, body: str, email_type: str = None) -> Dict:
    """
    便捷函数：使用LLM分析邮件内容
    
    Args:
        subject: 邮件主题
        body: 邮件正文
        email_type: 邮件类型
        
    Returns:
        分析结果
    """
    analyzer = LLMEmailAnalyzer()
    return analyzer.analyze_email_with_llm(subject, body, email_type)


if __name__ == "__main__":
    # 测试示例
    test_subject = "Invoice from Amazon Web Services - Payment Due"
    test_body = """
    Dear Customer,
    
    Invoice Number: INV-2024-001
    Issue Date: 2024-01-15
    Due Date: 2024-02-15
    
    Services Rendered:
    - EC2 Instance: $245.67
    - S3 Storage: $89.23
    - Data Transfer: $12.45
    
    Total Amount Due: $347.35 USD
    
    Please make payment by the due date.
    """
    
    result = analyze_email_content_llm(test_subject, test_body)
    print("LLM分析结果:")
    print(json.dumps(result, indent=2, ensure_ascii=False))