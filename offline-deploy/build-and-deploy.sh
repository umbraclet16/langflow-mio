#!/bin/bash
set -e

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DEPLOY_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "========================================"
echo "  Langflow 二次开发 - 构建部署"
echo "========================================"
echo ""

echo "[1/2] 构建自定义镜像 langflow-custom:latest ..."
docker build \
  -t langflow-custom:latest \
  -f "${DEPLOY_DIR}/Dockerfile.deploy" \
  "${PROJECT_ROOT}"

echo "[2/2] 启动服务 ..."
cd "${DEPLOY_DIR}/deploy"
docker compose up -d

echo ""
echo "部署完成！访问 http://localhost:7860"
