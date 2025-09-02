# 本地部署指南

## 本地开发环境设置

### 前置要求

```bash
# 必需软件
- Python 3.8+
- Docker Desktop
- AWS CLI
- Git

# 可选软件
- PostgreSQL (用于本地数据库)
- pgAdmin (数据库管理)
```

### 快速开始

```bash
# 1. 克隆项目
git clone <your-repo-url>
cd aws_agent_core

# 2. 设置虚拟环境
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# 或
.venv\\Scripts\\activate  # Windows

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置环境变量
cp .env.example .env
# 编辑 .env 文件配置您的设置
```

## 本地运行方式

### 方式一：使用Docker Compose（推荐）

```bash
# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 方式二：纯Python环境

```bash
# 激活虚拟环境
source .venv/bin/activate

# 启动应用
python -m customer_support

# 或者使用AgentCore SDK
agentcore launch --local
```

### 方式三：混合模式（Docker + 本地Python）

```bash
# 只启动数据库
docker-compose up db -d

# 本地运行应用
source .venv/bin/activate
python -m customer_support
```

## Docker Compose 配置

创建 `docker-compose.yml` 文件：

```yaml
version: '3.8'

services:
  # 主应用服务
  app:
    build: .
    ports:
      - "8080:8080"
      - "8000:8000"
    environment:
      - AWS_REGION=us-east-1
      - DATABASE_URL=postgresql://postgres:password@db:5432/financial_emails
      - MCP_ENABLED=false
    depends_on:
      - db
    volumes:
      - ./credentials.json:/app/credentials.json:ro
      - ./tokens:/app/tokens
    restart: unless-stopped

  # PostgreSQL数据库
  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=financial_emails
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    restart: unless-stopped

  # pgAdmin (数据库管理)
  pgadmin:
    image: dpage/pgadmin4
    environment:
      - PGADMIN_DEFAULT_EMAIL=admin@example.com
      - PGADMIN_DEFAULT_PASSWORD=admin
    ports:
      - "5050:80"
    depends_on:
      - db
    restart: unless-stopped

volumes:
  postgres_data:
  tokens:
```

## 数据库初始化

创建 `init.sql` 文件：

```sql
-- 创建数据库
CREATE DATABASE financial_emails;

-- 创建专用用户
CREATE USER financial_user WITH PASSWORD 'financial_password';
GRANT ALL PRIVILEGES ON DATABASE financial_emails TO financial_user;

-- 创建表结构
\c financial_emails

CREATE TABLE IF NOT EXISTS financial_emails (
    id SERIAL PRIMARY KEY,
    email_id VARCHAR(255) UNIQUE NOT NULL,
    subject TEXT NOT NULL,
    from_email TEXT NOT NULL,
    email_date TIMESTAMP,
    body_preview TEXT,
    document_type VARCHAR(50),
    status VARCHAR(50),
    counterparty TEXT,
    original_amount DECIMAL(15, 2),
    original_currency VARCHAR(10),
    usd_amount DECIMAL(15, 2),
    exchange_rate DECIMAL(10, 6),
    due_date TIMESTAMP,
    issue_date TIMESTAMP,
    start_date TIMESTAMP,
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    raw_data JSONB
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_financial_emails_email_id ON financial_emails(email_id);
CREATE INDEX IF NOT EXISTS idx_financial_emails_status ON financial_emails(status);
CREATE INDEX IF NOT EXISTS idx_financial_emails_document_type ON financial_emails(document_type);
CREATE INDEX IF NOT EXISTS idx_financial_emails_processed_at ON financial_emails(processed_at);

-- 授予权限
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO financial_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO financial_user;
```

## 环境变量配置

编辑 `.env` 文件：

```env
# 应用配置
AWS_REGION=us-east-1
LOG_LEVEL=DEBUG
PYTHONUNBUFFERED=1

# 数据库配置 (Docker Compose)
DATABASE_URL=postgresql://financial_user:financial_password@localhost:5432/financial_emails

# 或者本地PostgreSQL
# DATABASE_URL=postgresql://financial_user:financial_password@localhost:5432/financial_emails

# MCP配置
MCP_ENABLED=false
MCP_SERVER_URL=http://localhost:8000

# Gmail API配置
GMAIL_CREDENTIALS_FILE=credentials.json

# 可选：汇率API密钥
EXCHANGE_RATE_API_KEY=your_api_key_here
```

## 本地测试脚本

创建 `run_local.py` 脚本：

```python
#!/usr/bin/env python3
"""
本地运行脚本
"""
import os
import sys
import subprocess
import time
from pathlib import Path

def check_docker():
    """检查Docker是否运行"""
    try:
        result = subprocess.run(['docker', 'info'], 
                              capture_output=True, text=True)
        return result.returncode == 0
    except:
        return False

def start_services():
    """启动服务"""
    print("🚀 启动本地服务...")
    
    # 检查Docker
    if not check_docker():
        print("❌ Docker未运行，请启动Docker Desktop")
        return False
    
    # 启动Docker服务
    try:
        print("🐳 启动Docker容器...")
        subprocess.run(['docker-compose', 'up', '-d'], check=True)
        
        # 等待服务启动
        print("⏳ 等待服务启动...")
        time.sleep(5)
        
        # 检查服务状态
        result = subprocess.run(
            ['curl', '-f', 'http://localhost:8080/health'],
            capture_output=True
        )
        
        if result.returncode == 0:
            print("✅ 服务启动成功！")
            print("📊 应用地址: http://localhost:8080")
            print("🗄️  数据库管理: http://localhost:5050")
            print("📧 开始处理财务邮件吧！")
            return True
        else:
            print("❌ 服务启动失败")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ 启动失败: {e}")
        return False

def stop_services():
    """停止服务"""
    print("🛑 停止服务...")
    try:
        subprocess.run(['docker-compose', 'down'], check=True)
        print("✅ 服务已停止")
    except subprocess.CalledProcessError as e:
        print(f"❌ 停止失败: {e}")

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("使用方式: python run_local.py [start|stop|status]")
        return
    
    command = sys.argv[1]
    
    if command == 'start':
        start_services()
    elif command == 'stop':
        stop_services()
    elif command == 'status':
        check_status()
    else:
        print("无效命令")

if __name__ == "__main__":
    main()
```

## 本地测试命令

```bash
# 使脚本可执行
chmod +x run_local.py

# 启动服务
python run_local.py start

# 停止服务
python run_local.py stop

# 测试Agent功能
curl -X POST http://localhost:8080/2024-01-01/runtime/invoke \
  -H "Content-Type: application/json" \
  -d '{"prompt": "测试健康检查"}'

# 测试健康检查
curl http://localhost:8080/health

# 测试就绪检查
curl http://localhost:8080/ready
```

## 故障排除

### 常见问题

1. **端口冲突**
   ```bash
   # 查看占用端口的进程
   lsof -i :8080
   lsof -i :5432
   
   # 或者使用
   netstat -tulpn | grep :8080
   ```

2. **Docker权限问题**
   ```bash
   # 将用户添加到docker组
   sudo usermod -aG docker $USER
   
   # 重新登录生效
   newgrp docker
   ```

3. **数据库连接问题**
   ```bash
   # 测试数据库连接
   pg_isready -h localhost -p 5432 -U postgres
   ```

4. **内存不足**
   ```bash
   # 调整Docker内存限制
   # 在Docker Desktop设置中增加内存分配
   ```

### 调试模式

```bash
# 启用详细日志
export LOG_LEVEL=DEBUG

# 查看详细日志
docker-compose logs app

# 进入容器调试
docker-compose exec app bash

# 查看数据库
docker-compose exec db psql -U postgres financial_emails
```

## 开发工作流

### 典型开发流程

1. **启动开发环境**
   ```bash
   docker-compose up -d
   ```

2. **编写代码**
   ```bash
   # 在本地编辑文件
   code .
   ```

3. **测试更改**
   ```bash
   # 自动热重载（如果配置了volume映射）
   # 或者重新构建镜像
   docker-compose build app
   docker-compose up -d
   ```

4. **查看日志**
   ```bash
   docker-compose logs -f app
   ```

5. **运行测试**
   ```bash
   docker-compose exec app python -m pytest tests/
   ```

### 性能优化建议

1. **使用本地Volume加速开发**
   ```yaml
   volumes:
     - .:/app
     - /app/__pycache__  # 避免缓存同步
   ```

2. **配置开发模式**
   ```bash
   # 设置开发环境变量
   export ENVIRONMENT=development
   export PYTHONPATH=/app
   ```

3. **使用调试器**
   ```bash
   # 在代码中添加断点
   import pdb; pdb.set_trace()
   
   # 或者使用debugpy
   pip install debugpy
   python -m debugpy --listen 0.0.0.0:5678 -m customer_support
   ```

## 支持

如有本地部署问题，请检查：

1. Docker Desktop 是否运行
2. 端口是否被占用
3. 环境变量配置是否正确
4. 查看详细日志：`docker-compose logs`

享受本地开发！🎉