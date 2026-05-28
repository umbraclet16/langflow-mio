# 离线部署 Dockerfile - 所有依赖都包含在镜像中
# 使用国内镜像源构建

################################
# BUILDER - 构建阶段
################################
FROM python:3.12-bookworm AS builder
#FROM docker.xuanyuan.run/library/python:3.12-bookworm AS builder

# 使用国内 apt 源
RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources

# 安装构建依赖
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    git \
    curl \
    gnupg \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 安装 Node.js 20.x (使用国内镜像)
RUN ARCH=$(dpkg --print-architecture) \
    && if [ "$ARCH" = "amd64" ]; then NODE_ARCH="x64"; \
       elif [ "$ARCH" = "arm64" ]; then NODE_ARCH="arm64"; \
       else NODE_ARCH="$ARCH"; fi \
    && curl -fsSL "https://npmmirror.com/mirrors/node/v20.19.0/node-v20.19.0-linux-${NODE_ARCH}.tar.xz" \
    | tar -xJ -C /usr/local --strip-components=1

# 配置 npm 使用国内镜像
RUN npm config set registry https://registry.npmmirror.com

# 安装 uv 包管理器 (使用国内镜像)
RUN curl -LsSf https://gitee.com/mirrors_astral-sh/uv/raw/main/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

WORKDIR /app

# 设置环境变量
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV RUSTFLAGS='--cfg reqwest_unstable'

# 复制依赖定义文件
COPY pyproject.toml uv.lock README.md ./
COPY src/backend/base/pyproject.toml src/backend/base/README.md src/backend/base/
COPY src/lfx/pyproject.toml src/lfx/README.md src/lfx/
COPY src/sdk/pyproject.toml src/sdk/README.md src/sdk/

# 安装 Python 依赖
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-editable --extra postgresql --no-group dev

# 复制源代码
COPY src/backend src/backend
COPY src/lfx src/lfx
COPY src/sdk src/sdk

# 构建前端
COPY src/frontend /tmp/src/frontend
WORKDIR /tmp/src/frontend
RUN npm ci \
    && NODE_OPTIONS="--max-old-space-size=4096" npm run build \
    && cp -r build /app/src/backend/langflow/frontend \
    && rm -rf /tmp/src/frontend

WORKDIR /app

# 安装项目本身
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-editable --extra postgresql --no-group dev

################################
# RUNTIME - 运行阶段
################################
FROM python:3.12-bookworm AS runtime
#FROM docker.xuanyuan.run/library/python:3.12-bookworm AS runtime

# 使用国内 apt 源
RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources

# 安装运行时依赖
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    curl \
    git \
    libpq5 \
    gnupg \
    xz-utils \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 安装 Node.js (使用国内镜像)
RUN ARCH=$(dpkg --print-architecture) \
    && if [ "$ARCH" = "amd64" ]; then NODE_ARCH="x64"; \
       elif [ "$ARCH" = "arm64" ]; then NODE_ARCH="arm64"; \
       else NODE_ARCH="$ARCH"; fi \
    && curl -fsSL "https://npmmirror.com/mirrors/node/v20.19.0/node-v20.19.0-linux-${NODE_ARCH}.tar.xz" \
    | tar -xJ -C /usr/local --strip-components=1

# 复制 uv 工具
COPY --from=builder /root/.local/bin/uv /usr/local/bin/uv
COPY --from=builder /root/.local/bin/uvx /usr/local/bin/uvx

# 从构建阶段复制虚拟环境
COPY --from=builder /app/.venv /app/.venv

# 设置 PATH
ENV PATH="/app/.venv/bin:$PATH"

# 设置标签
LABEL org.opencontainers.image.title=langflow-offline
LABEL org.opencontainers.image.description="Langflow 离线部署镜像"
LABEL org.opencontainers.image.licenses=MIT

WORKDIR /app/data

# 暴露端口
EXPOSE 7860

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:7860/health || exit 1

# 启动命令
CMD ["python", "-m", "langflow", "run", "--host", "0.0.0.0", "--port", "7860"]
