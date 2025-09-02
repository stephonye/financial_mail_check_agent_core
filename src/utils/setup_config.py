#!/usr/bin/env python3
"""
AWS Bedrock AgentCore 配置初始化脚本
自动创建配置文件并替换占位符
"""

import os
import re
from pathlib import Path

def setup_configuration():
    """设置配置文件"""
    print("🔧 AWS Bedrock AgentCore 配置初始化")
    print("=" * 50)
    
    # 检查模板文件
    template_file = Path(".bedrock_agentcore.yaml.template")
    if not template_file.exists():
        print("❌ 模板文件不存在: .bedrock_agentcore.yaml.template")
        return False
    
    # 读取模板内容
    with open(template_file, 'r', encoding='utf-8') as f:
        template_content = f.read()
    
    # 获取用户输入
    aws_account_id = input("请输入您的AWS账户ID (12位数字): ").strip()
    
    # 验证账户ID格式
    if not re.match(r'^\d{12}$', aws_account_id):
        print("❌ AWS账户ID必须是12位数字")
        return False
    
    # 替换占位符
    config_content = template_content.replace('YOUR_ACCOUNT_ID', aws_account_id)
    
    # 写入配置文件
    config_file = Path(".bedrock_agentcore.yaml")
    if config_file.exists():
        backup_file = Path(".bedrock_agentcore.yaml.backup")
        if backup_file.exists():
            backup_file.unlink()  # 删除旧的备份
        config_file.rename(backup_file)
        print("📦 已备份现有配置文件")
    
    with open(config_file, 'w', encoding='utf-8') as f:
        f.write(config_content)
    
    print("✅ 配置文件创建成功: .bedrock_agentcore.yaml")
    print("📋 配置摘要:")
    print(f"   - AWS账户ID: {aws_account_id}")
    print(f"   - 区域: us-east-1")
    print(f"   - 执行角色: arn:aws:iam::{aws_account_id}:role/AmazonBedrockAgentCoreExecutionRole")
    print(f"   - ECR仓库: {aws_account_id}.dkr.ecr.us-east-1.amazonaws.com/financial-email-processor")
    
    # 检查环境变量文件
    env_example = Path(".env.example")
    env_file = Path(".env")
    
    if env_example.exists() and not env_file.exists():
        create_env = input("\n是否创建环境变量文件? (y/n): ").strip().lower()
        if create_env == 'y':
            with open(env_example, 'r', encoding='utf-8') as src, open(env_file, 'w', encoding='utf-8') as dst:
                dst.write(src.read())
            print("✅ 环境变量文件创建成功: .env")
            print("📝 请编辑 .env 文件配置数据库和其他设置")
    
    print("\n🎉 配置完成!")
    print("下一步:")
    print("  1. 编辑 .env 文件配置环境变量")
    print("  2. 配置AWS CLI: aws configure")
    print("  3. 运行部署: ./deploy.sh")
    print("=" * 50)
    
    return True

def validate_aws_config():
    """验证AWS配置"""
    print("\n🔍 验证AWS配置...")
    
    # 检查AWS CLI是否安装
    try:
        import subprocess
        result = subprocess.run(['aws', '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("✅ AWS CLI 已安装")
        else:
            print("⚠️  AWS CLI 未安装或配置")
            print("   请运行: curl 'https://awscli.amazonaws.com/AWSCLIV2.pkg' -o 'AWSCLIV2.pkg' && sudo installer -pkg AWSCLIV2.pkg -target /")
    except (FileNotFoundError, subprocess.TimeoutExpired):
        print("⚠️  AWS CLI 未安装")
    
    # 检查配置文件
    config_file = Path(".bedrock_agentcore.yaml")
    if config_file.exists():
        with open(config_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'YOUR_ACCOUNT_ID' in content:
            print("❌ 配置文件中仍有占位符，请运行设置脚本")
            return False
        else:
            print("✅ 配置文件已正确配置")
            return True
    else:
        print("❌ 配置文件不存在")
        return False

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='AWS Bedrock AgentCore 配置工具')
    parser.add_argument('--setup', action='store_true', help='初始化配置')
    parser.add_argument('--validate', action='store_true', help='验证配置')
    parser.add_argument('--account-id', help='AWS账户ID')
    
    args = parser.parse_args()
    
    if args.setup:
        if args.account_id:
            # 通过命令行参数设置
            os.environ['AWS_ACCOUNT_ID'] = args.account_id
        setup_configuration()
    elif args.validate:
        validate_aws_config()
    else:
        print("使用方式:")
        print("  python setup_config.py --setup           # 交互式配置")
        print("  python setup_config.py --setup --account-id 123456789012  # 非交互式配置")
        print("  python setup_config.py --validate        # 验证配置")

if __name__ == "__main__":
    main()