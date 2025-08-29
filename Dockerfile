FROM public.ecr.aws/docker/library/python:3.12-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt ./

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 安装AWS OpenTelemetry分布式追踪
RUN pip install aws-opentelemetry-distro>=0.10.0

# 设置环境变量
ENV AWS_REGION=us-east-1
ENV AWS_DEFAULT_REGION=us-east-1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# 标识Docker容器运行环境
ENV DOCKER_CONTAINER=1

# 创建非root用户
RUN useradd -m -u 1000 bedrock_agentcore && \
    chown -R bedrock_agentcore:bedrock_agentcore /app

# 切换用户
USER bedrock_agentcore

# 暴露端口
EXPOSE 8080  # AgentCore HTTP端口
EXPOSE 8000  # 可选：调试端口

# 复制项目文件
COPY --chown=bedrock_agentcore:bedrock_agentcore . .

# 健康检查
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# 启动命令 - 使用opentelemetry-instrument进行分布式追踪
CMD ["opentelemetry-instrument", "python", "-m", "customer_support"]
