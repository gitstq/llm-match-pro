FROM python:3.11-slim

LABEL maintainer="gitstq"
LABEL description="LLM-Match-Pro: 智能本地LLM硬件匹配与推荐引擎"

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目代码
COPY llm_match_pro/ ./llm_match_pro/
COPY pyproject.toml .

# 安装项目
RUN pip install -e .

# 暴露Web端口
EXPOSE 8501

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import llm_match_pro" || exit 1

# 默认启动CLI
ENTRYPOINT ["llm-match-pro"]
CMD ["--help"]
