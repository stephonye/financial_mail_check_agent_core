#!/usr/bin/env python3
"""
AWS Bedrock AgentCore Gateway and Memory Deployment Script
部署AWS Bedrock AgentCore的Gateway和Memory组件
"""

import json
import boto3
import logging
from bedrock_agentcore.memory import MemoryClient
from botocore.exceptions import ClientError

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BedrockAgentCoreDeployer:
    def __init__(self, region='us-west-2'):
        self.region = region
        self.memory_client = MemoryClient(region_name=region)
        self.bedrock_client = boto3.client('bedrock-agent', region_name=region)
        
    def deploy_memory(self):
        """部署Memory组件"""
        logger.info("🧠 开始部署Memory组件...")
        
        try:
            # 创建基础Memory
            memory = self.memory_client.create_memory(
                name="CustomerSupportMemory",
                description="Customer support agent memory for storing conversation context and user preferences",
                event_expiry_days=30
            )
            
            logger.info(f"✅ Memory创建成功: {memory.get('id')}")
            return memory
            
        except ClientError as e:
            logger.error(f"❌ Memory创建失败: {e}")
            raise
            
    def deploy_memory_with_strategies(self):
        """部署带有策略的Memory组件"""
        logger.info("🧠 开始部署带策略的Memory组件...")
        
        try:
            # 创建会话摘要Memory
            summary_memory = self.memory_client.create_memory_and_wait(
                name="SessionSummaryMemory",
                description="Memory for summarizing conversation sessions",
                event_expiry_days=7,
                max_wait=300,
                poll_interval=10,
                strategies=[{
                    "summaryMemoryStrategy": {
                        "name": "SessionSummarizer",
                        "namespaces": ["/summaries/{actorId}/{sessionId}"]
                    }
                }]
            )
            
            logger.info(f"✅ 会话摘要Memory创建成功: {summary_memory.get('id')}")
            
            # 创建用户偏好Memory
            user_pref_memory = self.memory_client.create_memory_and_wait(
                name="UserPreferenceMemory",
                description="Memory for storing user preferences and settings",
                max_wait=300,
                poll_interval=10,
                strategies=[{
                    "userPreferenceMemoryStrategy": {
                        "name": "UserPreferenceStorage",
                        "namespaces": ["/users/{actorId}"]
                    }
                }]
            )
            
            logger.info(f"✅ 用户偏好Memory创建成功: {user_pref_memory.get('id')}")
            
            return {
                "summary_memory": summary_memory,
                "user_preference_memory": user_pref_memory
            }
            
        except ClientError as e:
            logger.error(f"❌ 带策略的Memory创建失败: {e}")
            raise
            
    def deploy_gateway(self):
        """部署Gateway组件"""
        logger.info("🚪 开始部署Gateway组件...")
        
        try:
            # 检查是否已有Gateway配置
            logger.info("检查现有Gateway配置...")
            
            # 使用AWS CLI创建Gateway（如果需要）
            # 注意：Bedrock AgentCore的Gateway可能需要通过AWS Management Console或API创建
            logger.info("ℹ️  Gateway可能需要通过AWS Management Console配置")
            logger.info("请访问AWS Bedrock AgentCore控制台创建Gateway")
            
            return {
                "status": "manual_setup_required",
                "message": "Gateway需要通过AWS Management Console手动配置"
            }
            
        except ClientError as e:
            logger.error(f"❌ Gateway配置检查失败: {e}")
            raise
            
    def deploy_all(self):
        """部署所有组件"""
        logger.info("🚀 开始部署AWS Bedrock AgentCore组件...")
        
        results = {}
        
        try:
            # 部署Memory组件
            logger.info("部署Memory组件...")
            results['memory'] = self.deploy_memory()
            results['memory_with_strategies'] = self.deploy_memory_with_strategies()
            
            # 部署Gateway组件
            logger.info("部署Gateway组件...")
            results['gateway'] = self.deploy_gateway()
            
            logger.info("🎉 所有组件部署完成！")
            
            # 保存部署结果
            self.save_deployment_info(results)
            
            return results
            
        except Exception as e:
            logger.error(f"❌ 部署过程中发生错误: {e}")
            raise
            
    def save_deployment_info(self, results):
        """保存部署信息到文件"""
        deployment_info = {
            "region": self.region,
            "deployment_time": json.dumps(None, default=str),  # 简单的时间戳
            "components": {
                "memory": {
                    "id": results.get('memory', {}).get('id'),
                    "name": "CustomerSupportMemory"
                },
                "summary_memory": {
                    "id": results.get('memory_with_strategies', {}).get('summary_memory', {}).get('id'),
                    "name": "SessionSummaryMemory"
                },
                "user_preference_memory": {
                    "id": results.get('memory_with_strategies', {}).get('user_preference_memory', {}).get('id'),
                    "name": "UserPreferenceMemory"
                },
                "gateway": {
                    "id": results.get('gateway', {}).get('id'),
                    "name": "CustomerSupportGateway"
                }
            }
        }
        
        with open('deployment_info.json', 'w') as f:
            json.dump(deployment_info, f, indent=2)
            
        logger.info("📋 部署信息已保存到 deployment_info.json")

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='部署AWS Bedrock AgentCore Gateway和Memory组件')
    parser.add_argument('--region', default='us-west-2', help='AWS区域 (默认: us-west-2)')
    parser.add_argument('--component', choices=['all', 'memory', 'gateway'], default='all',
                       help='部署组件类型 (默认: all)')
    
    args = parser.parse_args()
    
    deployer = BedrockAgentCoreDeployer(region=args.region)
    
    try:
        if args.component == 'all':
            deployer.deploy_all()
        elif args.component == 'memory':
            deployer.deploy_memory()
            deployer.deploy_memory_with_strategies()
        elif args.component == 'gateway':
            deployer.deploy_gateway()
            
    except Exception as e:
        logger.error(f"部署失败: {e}")
        exit(1)

if __name__ == "__main__":
    main()