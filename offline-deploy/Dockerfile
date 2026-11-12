# 二次开发镜像 Dockerfile（离线构建）
# 用法: 在项目根目录执行 docker build -t langflow-custom:latest -f offline-deploy/Dockerfile .
# 原理: 以官方镜像为底,把仓库源码与宿主机已构建好的前端产物直接覆盖进 site-packages,
#       不执行 npm ci / npm run build / uv install,构建全程无需网络。
# 前置条件:
#   1. 本机已有 langflowai/langflow:1.9.3 基础镜像（离线机先在有网机器 docker save,再 docker load）
#   2. src/frontend/build/ 已存在（仓库根目录 make frontend 的产物）
# 说明: 与 dev/docker-compose.yml 的挂载目录一一对应;版本元数据仍为官方 1.9.3（与 dev 挂载一致）

FROM langflowai/langflow:1.9.3

USER root

# 干净替换三个后端包:先删除镜像内自带代码,再复制仓库源码（避免残留已删除的旧文件）
RUN rm -rf /app/.venv/lib/python3.14/site-packages/langflow \
           /app/.venv/lib/python3.14/site-packages/lfx \
           /app/.venv/lib/python3.14/site-packages/langflow_sdk

COPY src/backend/base/langflow/ /app/.venv/lib/python3.14/site-packages/langflow/
COPY src/lfx/src/lfx/ /app/.venv/lib/python3.14/site-packages/lfx/
COPY src/sdk/src/langflow_sdk/ /app/.venv/lib/python3.14/site-packages/langflow_sdk/

# 前端:直接使用宿主机已构建好的产物（src/frontend/build）,不在镜像内构建。
# 仓库源码里 langflow/frontend 是旧产物,先 COPY 到临时目录,再整体替换,避免新旧产物混杂
COPY src/frontend/build/ /app/.venv/lib/python3.14/site-packages/langflow/frontend.tmp/
RUN rm -rf /app/.venv/lib/python3.14/site-packages/langflow/frontend \
    && mv /app/.venv/lib/python3.14/site-packages/langflow/frontend.tmp \
          /app/.venv/lib/python3.14/site-packages/langflow/frontend

# 全程 root 运行,避免 volume 挂载权限问题
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:7860/health || exit 1

CMD ["python", "-m", "langflow", "run", "--host", "0.0.0.0", "--port", "7860"]
