#!/usr/bin/env python3
"""
Financial Email Processor - 本地运行脚本
支持一键启动/停止本地开发环境
"""

import os
import sys
import time
import subprocess
from pathlib import Path

def print_banner():
    """打印欢迎横幅"""
    banner = """
███████╗██╗███╗   ██╗ █████╗ ███╗   ██╗ ██████╗ ██╗ █████╗ ██╗     
██╔════╝██║████╗  ██║██╔══██╗████╗  ██║██╔════╝ ██║██╔══██╗██║     
█████╗  ██║██╔██╗ ██║███████║██╔██╗ ██║██║  ███╗██║███████║██║     
██╔══╝  ██║██║╚██╗██║██╔══██║██║╚██╗██║██║   ██║██║██╔══██║██║     
██║     ██║██║ ╚████║██║  ██║██║ ╚████║╚██████╔╝██║██║  ██║███████╗
╚═╝     ╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝╚═╝  ╚═══╝ ╚═════╝ ╚═╝╚═╝  ╚═╝╚══════╝
                                                                  
    🚀 Financial Email Processor - 本地开发环境
    """
    print(banner)

def check_docker():
    """检查Docker是否运行"""
    try:
        result = subprocess.run(['docker', 'info'], 
                              capture_output=True, text=True, timeout=10)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.CalledProcessError):
        return False

def check_docker_compose():
    """检查Docker Compose是否可用"""
    try:
        result = subprocess.run(['docker-compose', '--version'], 
                              capture_output=True, text=True, timeout=5)
        return result.returncode == 0
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False

def start_services():
    """启动所有服务"""
    print("🚀 启动本地开发环境...")
    
    # 检查Docker
    if not check_docker():
        print("❌ Docker未运行，请启动Docker Desktop")
        return False
    
    if not check_docker_compose():
        print("❌ Docker Compose不可用")
        return False
    
    # 检查配置文件
    if not Path(".env").exists():
        print("⚠️  环境配置文件 .env 不存在")
        if Path(".env.example").exists():
            print("📋 从模板创建配置文件...")
            subprocess.run(['cp', '.env.example', '.env'], check=True)
            print("✅ 请编辑 .env 文件配置您的设置")
        else:
            print("❌ 缺少环境配置文件")
            return False
    
    # 启动服务
    try:
        print("🐳 启动Docker容器...")
        result = subprocess.run(['docker-compose', 'up', '-d'], 
                              capture_output=True, text=True, timeout=120)
        
        if result.returncode != 0:
            print(f"❌ 启动失败: {result.stderr}")
            return False
        
        # 等待服务启动
        print("⏳ 等待服务启动...")
        time.sleep(8)
        
        # 检查服务健康状态
        print("🔍 检查服务状态...")
        
        # 检查应用健康
        try:
            health_result = subprocess.run(
                ['curl', '-s', '-f', 'http://localhost:8080/health'],
                capture_output=True, text=True, timeout=10
            )
            
            if health_result.returncode == 0:
                print("✅ 应用服务健康")
            else:
                print("❌ 应用服务异常")
                return False
                
        except subprocess.TimeoutExpired:
            print("⚠️  应用服务启动较慢，继续等待...")
            time.sleep(5)
        
        # 显示服务信息
        print("\n" + "="*50)
        print("✅ 本地开发环境启动成功！")
        print("="*50)
        print("📊 应用服务: http://localhost:8080")
        print("🗄️  数据库管理: http://localhost:5050")
        print("👤 pgAdmin账号: admin@financial.com / admin123")
        print("🔧 数据库连接: postgresql://financial_user:financial_password@localhost:5432/financial_emails")
        print("\n📝 下一步:")
        print("  1. 访问 http://localhost:8080 测试应用")
        print("  2. 使用 pgAdmin 管理数据库")
        print("  3. 运行 'python run_local.py stop' 停止服务")
        print("="*50)
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 启动失败: {e}")
        print(f"详细错误: {e.stderr}")
        return False
    except subprocess.TimeoutExpired:
        print("❌ 启动超时")
        return False

def stop_services():
    """停止所有服务"""
    print("🛑 停止本地开发环境...")
    
    if not check_docker_compose():
        print("❌ Docker Compose不可用")
        return False
    
    try:
        result = subprocess.run(['docker-compose', 'down'], 
                              capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print("✅ 服务已停止")
            return True
        else:
            print(f"❌ 停止失败: {result.stderr}")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ 停止失败: {e}")
        return False

def check_status():
    """检查服务状态"""
    print("🔍 检查服务状态...")
    
    if not check_docker_compose():
        print("❌ Docker Compose不可用")
        return False
    
    try:
        # 查看容器状态
        result = subprocess.run(['docker-compose', 'ps'], 
                              capture_output=True, text=True, timeout=10)
        print(result.stdout)
        
        # 检查应用健康
        try:
            health_result = subprocess.run(
                ['curl', '-s', 'http://localhost:8080/health'],
                capture_output=True, text=True, timeout=5
            )
            if health_result.returncode == 0:
                print("✅ 应用健康检查通过")
            else:
                print("❌ 应用健康检查失败")
        except:
            print("❌ 无法连接应用")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 状态检查失败: {e}")
        return False

def view_logs():
    """查看日志"""
    print("📋 查看应用日志...")
    
    if not check_docker_compose():
        print("❌ Docker Compose不可用")
        return False
    
    try:
        subprocess.run(['docker-compose', 'logs', '-f', 'app'], timeout=30)
    except subprocess.TimeoutExpired:
        print("\n⏹️  日志查看结束")
    except KeyboardInterrupt:
        print("\n⏹️  用户中断")

def main():
    """主函数"""
    print_banner()
    
    if len(sys.argv) < 2:
        print("使用方式: python run_local.py [command]")
        print("")
        print("命令:")
        print("  start   - 启动本地开发环境")
        print("  stop    - 停止本地开发环境")
        print("  status  - 查看服务状态")
        print("  logs    - 查看应用日志")
        print("  help    - 显示帮助信息")
        return
    
    command = sys.argv[1].lower()
    
    if command == 'start':
        start_services()
    elif command == 'stop':
        stop_services()
    elif command == 'status':
        check_status()
    elif command == 'logs':
        view_logs()
    elif command == 'help':
        print("详细文档请查看 LOCAL_DEPLOYMENT.md")
    else:
        print(f"❌ 未知命令: {command}")
        print("使用 'python run_local.py help' 查看帮助")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⏹️  用户中断")
    except Exception as e:
        print(f"❌ 发生错误: {e}")
        sys.exit(1)