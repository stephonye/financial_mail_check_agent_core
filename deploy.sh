#!/bin/bash

# AWS Bedrock AgentCore 部署脚本
set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查前置条件
check_prerequisites() {
    log_info "检查前置条件..."
    
    # 检查AWS CLI
    if ! command -v aws &> /dev/null; then
        log_error "AWS CLI 未安装"
        exit 1
    fi
    
    # 检查Bedrock AgentCore SDK
    if ! command -v agentcore &> /dev/null; then
        log_error "Bedrock AgentCore SDK 未安装"
        exit 1
    fi
    
    # 检查Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker 未安装"
        exit 1
    fi
    
    # 检查配置文件
    if [ ! -f ".bedrock_agentcore.yaml" ]; then
        log_warn "配置文件 .bedrock_agentcore.yaml 不存在"
        log_info "正在创建配置文件模板..."
        cp .bedrock_agentcore.yaml.template .bedrock_agentcore.yaml
        log_warn "请编辑 .bedrock_agentcore.yaml 文件配置您的AWS账户信息"
        exit 1
    fi
    
    log_info "前置条件检查通过"
}

# 本地测试
local_test() {
    log_info "运行本地测试..."
    
    # 构建Docker镜像
    log_info "构建Docker镜像..."
    docker build -t financial-email-processor .
    
    # 运行测试
    log_info "启动本地容器..."
    docker run -d -p 8080:8080 --name financial-email-processor-test financial-email-processor
    
    # 等待容器启动
    sleep 5
    
    # 测试健康检查
    if curl -f http://localhost:8080/health; then
        log_info "本地测试成功"
    else
        log_error "本地测试失败"
        docker logs financial-email-processor-test
        exit 1
    fi
    
    # 清理测试容器
    docker stop financial-email-processor-test
    docker rm financial-email-processor-test
}

# 部署到AWS
deploy_to_aws() {
    local environment=${1:-"development"}
    
    log_info "部署到AWS Bedrock AgentCore (环境: $environment)..."
    
    # 检查AWS认证
    if ! aws sts get-caller-identity &> /dev/null; then
        log_error "AWS认证失败，请配置AWS CLI"
        exit 1
    fi
    
    # 执行部署
    if [ "$environment" = "production" ]; then
        agentcore launch --env production
    else
        agentcore launch
    fi
    
    log_info "部署完成"
}

# 查看部署状态
check_status() {
    log_info "检查部署状态..."
    agentcore status
}

# 查看日志
view_logs() {
    local follow=${1:-false}
    
    if [ "$follow" = true ]; then
        log_info "实时查看日志 (Ctrl+C 退出)..."
        agentcore logs --follow
    else
        log_info "查看最近日志..."
        agentcore logs
    fi
}

# 主函数
main() {
    local command=${1:-"deploy"}
    local environment=${2:-"development"}
    
    case "$command" in
        "test")
            check_prerequisites
            local_test
            ;;
        "deploy")
            check_prerequisites
            local_test
            deploy_to_aws "$environment"
            ;;
        "status")
            check_status
            ;;
        "logs")
            view_logs "$environment"
            ;;
        "help"|"")
            echo "使用方式: $0 [command] [environment]"
            echo ""
            echo "命令:"
            echo "  test        - 运行本地测试"
            echo "  deploy      - 部署到AWS (默认)"
            echo "  status      - 查看部署状态"
            echo "  logs        - 查看日志"
            echo "  help        - 显示帮助信息"
            echo ""
            echo "环境:"
            echo "  development - 开发环境 (默认)"
            echo "  production  - 生产环境"
            ;;
        *)
            log_error "未知命令: $command"
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@"