#!/usr/bin/env python3
"""
AWS Bedrock AgentCore Gateway and Memory Status Check Script
检查Gateway和Memory组件的部署状态
"""

import json
import boto3
import logging
from bedrock_agentcore.memory import MemoryClient
from botocore.exceptions import ClientError

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_memory_status(region='us-west-2'):
    """检查Memory组件状态"""
    logger.info("🧠 检查Memory组件状态...")
    
    try:
        client = MemoryClient(region_name=region)
        memories = client.list_memories()
        
        logger.info(f"找到 {len(memories)} 个Memory组件:")
        
        memory_info = []
        for memory in memories:
            memory_id = memory.get('id')
            name = memory.get('name', 'N/A')
            status = memory.get('status', 'N/A')
            created_time = memory.get('createdTime', 'N/A')
            
            logger.info(f"  - {name} ({memory_id}): {status}")
            memory_info.append({
                'id': memory_id,
                'name': name,
                'status': status,
                'created_time': created_time
            })
        
        return memory_info
        
    except ClientError as e:
        logger.error(f"❌ 检查Memory状态失败: {e}")
        return []

def check_gateway_configuration(region='us-west-2'):
    """检查Gateway配置"""
    logger.info("🚪 检查Gateway配置...")
    
    try:
        # 检查Bedrock Agent配置
        bedrock_client = boto3.client('bedrock-agent', region_name=region)
        
        # 列出agents
        agents = bedrock_client.list_agents()
        logger.info(f"找到 {len(agents.get('agentSummaries', []))} 个Bedrock Agents:")
        
        gateway_info = []
        for agent in agents.get('agentSummaries', []):
            agent_id = agent.get('agentId')
            name = agent.get('agentName')
            status = agent.get('agentStatus')
            logger.info(f"  - {name} ({agent_id}): {status}")
            
            gateway_info.append({
                'id': agent_id,
                'name': name,
                'status': status,
                'type': 'bedrock_agent'
            })
        
        return gateway_info
        
    except ClientError as e:
        logger.error(f"❌ 检查Gateway配置失败: {e}")
        return []

def generate_deployment_summary(memory_info, gateway_info):
    """生成部署摘要"""
    logger.info("📋 生成部署摘要...")
    
    summary = {
        'deployment_status': {
            'memory': {
                'total_count': len(memory_info),
                'active_count': len([m for m in memory_info if m.get('status') == 'ACTIVE']),
                'creating_count': len([m for m in memory_info if m.get('status') == 'CREATING']),
                'components': memory_info
            },
            'gateway': {
                'total_count': len(gateway_info),
                'available_count': len([g for g in gateway_info if g.get('status') == 'READY']),
                'components': gateway_info
            }
        }
    }
    
    # 保存摘要到文件
    with open('deployment_summary.json', 'w') as f:
        json.dump(summary, f, indent=2)
    
    logger.info("📄 部署摘要已保存到 deployment_summary.json")
    
    # 打印摘要
    logger.info("\n" + "="*50)
    logger.info("🚀 DEPLOYMENT SUMMARY")
    logger.info("="*50)
    logger.info(f"Memory组件: {summary['deployment_status']['memory']['active_count']}/{summary['deployment_status']['memory']['total_count']} 活跃")
    logger.info(f"Gateway组件: {summary['deployment_status']['gateway']['available_count']}/{summary['deployment_status']['gateway']['total_count']} 可用")
    
    if summary['deployment_status']['memory']['creating_count'] > 0:
        logger.info(f"⏳ 有 {summary['deployment_status']['memory']['creating_count']} 个Memory组件仍在创建中")
    
    logger.info("="*50)
    
    return summary

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='检查AWS Bedrock AgentCore Gateway和Memory组件状态')
    parser.add_argument('--region', default='us-west-2', help='AWS区域 (默认: us-west-2)')
    
    args = parser.parse_args()
    
    logger.info(f"🔍 检查区域: {args.region}")
    
    # 检查Memory状态
    memory_info = check_memory_status(args.region)
    
    # 检查Gateway配置
    gateway_info = check_gateway_configuration(args.region)
    
    # 生成部署摘要
    summary = generate_deployment_summary(memory_info, gateway_info)
    
    logger.info("✅ 状态检查完成")

if __name__ == "__main__":
    main()