#!/usr/bin/env python3
"""
LLM增强功能测试脚本
"""
import json
from llm_email_analyzer import LLMEmailAnalyzer, analyze_email_content_llm

def test_llm_analyzer():
    """测试LLM邮件分析器"""
    print("🧪 测试LLM邮件分析器...")
    
    # 测试数据
    test_cases = [
        {
            "subject": "Invoice from Amazon Web Services - Payment Due",
            "body": """
            Invoice Number: INV-2024-001
            Issue Date: January 15, 2024
            Due Date: February 15, 2024
            
            Services Rendered:
            - EC2 Instance: $245.67
            - S3 Storage: $89.23
            - Data Transfer: $12.45
            
            Total Amount Due: $347.35 USD
            
            Please make payment by the due date.
            """,
            "type": "invoice"
        },
        {
            "subject": "Purchase Order Confirmation - Order #PO-12345",
            "body": """
            Thank you for your order!
            
            Order Details:
            - Product: Laptop Pro 15\"
            - Quantity: 2
            - Unit Price: €1,299.00
            - Total: €2,598.00 EUR
            
            Expected Delivery: 2024-01-25
            """,
            "type": "order"
        },
        {
            "subject": "Monthly Bank Statement - December 2023",
            "body": """
            Account Statement Period: Dec 1 - Dec 31, 2023
            
            Transactions:
            - Dec 5: Payment received ¥50,000.00
            - Dec 15: Withdrawal ¥12,345.00
            - Dec 28: Transfer ¥8,888.00
            
            Closing Balance: ¥125,467.00 JPY
            """,
            "type": "statement"
        }
    ]
    
    analyzer = LLMEmailAnalyzer()
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📧 测试用例 {i}: {test_case['type'].upper()}")
        print(f"主题: {test_case['subject']}")
        
        try:
            # 使用LLM分析
            result = analyzer.analyze_email_with_llm(
                test_case['subject'], 
                test_case['body'], 
                test_case['type']
            )
            
            print(f"✅ 分析成功 - 置信度: {result.get('confidence', 0):.2f}")
            print(f"文档类型: {result.get('document_type')}")
            print(f"交易对手: {result.get('counterparty')}")
            print(f"金额: {result.get('amount')} {result.get('currency')}")
            print(f"USD金额: {result.get('usd_amount')}")
            print(f"分析方式: {result.get('analysis_method')}")
            
            # 显示异常检测
            anomalies = result.get('anomalies', [])
            if anomalies:
                print(f"⚠️  异常检测: {anomalies}")
            
        except Exception as e:
            print(f"❌ 分析失败: {e}")

def test_direct_function():
    """测试直接调用函数"""
    print("\n🔧 测试直接调用函数...")
    
    subject = "Payment Receipt from Google Cloud Platform"
    body = """
    Receipt for Payment
    Date: 2024-01-10
    Amount: $1,234.56 USD
    Payment Method: Credit Card
    Transaction ID: TXN-987654321
    
    Thank you for your business!
    """
    
    try:
        result = analyze_email_content_llm(subject, body, "receipt")
        print("✅ 直接调用成功")
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"❌ 直接调用失败: {e}")

def test_fallback_scenario():
    """测试回退场景"""
    print("\n🔄 测试回退场景...")
    
    # 使用非常规格式的邮件
    subject = "Important Notice"
    body = "This is a test email without clear financial information."
    
    try:
        result = analyze_email_content_llm(subject, body)
        print(f"✅ 回退分析完成 - 置信度: {result.get('confidence', 0):.2f}")
        print(f"分析方式: {result.get('analysis_method')}")
    except Exception as e:
        print(f"❌ 回退测试失败: {e}")

if __name__ == "__main__":
    print("🚀 开始LLM增强功能测试")
    print("=" * 50)
    
    test_llm_analyzer()
    test_direct_function()
    test_fallback_scenario()
    
    print("\n" + "=" * 50)
    print("✅ LLM增强功能测试完成")