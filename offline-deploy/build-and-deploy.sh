#!/bin/bash
set -e

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DEPLOY_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "========================================"
echo "  Langflow 二次开发 - 构建部署"
echo "========================================"
echo ""

# 前置检查:前端产物(镜像构建不执行 npm,直接用宿主机产物)
if [ ! -d "${PROJECT_ROOT}/src/frontend/build" ]; then
  echo "错误: 未找到 ${PROJECT_ROOT}/src/frontend/build"
  echo "请先在仓库根目录构建前端: make frontend (或 cd src/frontend && npm ci && npm run build)"
  exit 1
fi

# 前置检查:基础镜像(离线环境需先 docker load)
if ! docker image inspect langflowai/langflow:1.9.3 >/dev/null 2>&1; then
  echo "错误: 本机没有 langflowai/langflow:1.9.3 基础镜像"
  echo "离线环境请先在有网机器 docker pull 并 docker save,再到本机 docker load"
  exit 1
fi

echo "[1/2] 构建自定义镜像 langflow-custom:latest ..."
docker build \
  -t langflow-custom:latest \
  -f "${DEPLOY_DIR}/Dockerfile" \
  "${PROJECT_ROOT}"

echo "[2/2] 启动服务 ..."
cd "${DEPLOY_DIR}/deploy"
docker compose up -d

echo ""
echo "部署完成！访问 http://localhost:7860"
