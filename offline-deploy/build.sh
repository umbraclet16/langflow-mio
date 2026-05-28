#!/bin/bash
# Langflow 离线部署 - 镜像构建脚本
# 此脚本在有网络的环境中运行，用于构建离线部署所需的 Docker 镜像
# 使用国内镜像源加速构建

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 项目根目录
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DEPLOY_DIR="$(cd "$(dirname "$0")" && pwd)"

echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}          Langflow 离线部署 - 镜像构建工具                    ${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
echo ""

# 检查 Docker 是否可用
if ! command -v docker &> /dev/null; then
    echo -e "${RED}错误: 未安装 Docker${NC}"
    exit 1
fi

# 检查并配置 Docker 镜像加速
echo -e "${YELLOW}检查 Docker 镜像配置...${NC}"
DAEMON_JSON="/etc/docker/daemon.json"
if [ -f "${DEPLOY_DIR}/daemon.json" ]; then
    if [ ! -f "${DAEMON_JSON}" ] || ! grep -q "registry-mirrors" "${DAEMON_JSON}" 2>/dev/null; then
        echo -e "${YELLOW}提示: 建议配置 Docker 镜像加速以提升构建速度${NC}"
        echo -e "执行以下命令配置轩辕镜像加速:"
        echo -e "  sudo cp ${DEPLOY_DIR}/daemon.json ${DAEMON_JSON}"
        echo -e "  sudo systemctl restart docker"
        echo ""
    fi
fi

echo -e "${YELLOW}步骤 1/4: 复制项目文件到构建上下文...${NC}"

# 创建临时构建目录
BUILD_TEMP="${DEPLOY_DIR}/.build-context"
rm -rf "${BUILD_TEMP}"
mkdir -p "${BUILD_TEMP}"

# 复制必要的项目文件
cp -r "${PROJECT_ROOT}/src" "${BUILD_TEMP}/"
cp "${PROJECT_ROOT}/pyproject.toml" "${BUILD_TEMP}/"
cp "${PROJECT_ROOT}/uv.lock" "${BUILD_TEMP}/"
cp "${PROJECT_ROOT}/README.md" "${BUILD_TEMP}/"

echo -e "${GREEN}✓ 项目文件已复制${NC}"

echo -e "${YELLOW}步骤 2/4: 构建 Langflow 离线镜像...${NC}"

# 复制 Dockerfile 到构建目录
cp "${DEPLOY_DIR}/Dockerfile" "${BUILD_TEMP}/"

# 构建镜像
docker build \
    --tag langflow-offline:latest \
    --tag langflow-offline:$(grep '^version' "${PROJECT_ROOT}/pyproject.toml" | sed 's/.*"\(.*\)"/\1/') \
    "${BUILD_TEMP}"

if [ $? -ne 0 ]; then
    echo -e "${RED}错误: 镜像构建失败${NC}"
    rm -rf "${BUILD_TEMP}"
    exit 1
fi

echo -e "${GREEN}✓ Langflow 镜像构建成功${NC}"

echo -e "${YELLOW}步骤 3/4: 拉取 PostgreSQL 镜像...${NC}"

# 拉取 PostgreSQL 镜像（用于离线部署）
#docker pull postgres:16-bookworm
docker pull  docker.xuanyuan.run/library/postgres:16-bookworm
docker tag  docker.xuanyuan.run/library/postgres:16-bookworm postgres:16-bookworm

echo -e "${GREEN}✓ PostgreSQL 镜像已准备${NC}"

echo -e "${YELLOW}步骤 4/4: 保存镜像到离线包...${NC}"

# 创建输出目录
OUTPUT_DIR="${DEPLOY_DIR}/dist"
mkdir -p "${OUTPUT_DIR}"

# 获取版本号
VERSION=$(grep '^version' "${PROJECT_ROOT}/pyproject.toml" | sed 's/.*"\(.*\)"/\1/')

# 保存镜像为 tar 文件
echo "正在保存 langflow-offline 镜像..."
docker save langflow-offline:latest | gzip > "${OUTPUT_DIR}/langflow-offline.tar.gz"

echo "正在保存 postgres 镜像..."
docker save postgres:16-bookworm | gzip > "${OUTPUT_DIR}/postgres-16.tar.gz"

# 复制部署文件
cp "${DEPLOY_DIR}/docker-compose.yml" "${OUTPUT_DIR}/"
cp "${DEPLOY_DIR}/deploy.sh" "${OUTPUT_DIR}/"
cp "${DEPLOY_DIR}/README.md" "${OUTPUT_DIR}/"

# 清理临时目录
rm -rf "${BUILD_TEMP}"

# 计算包大小
TOTAL_SIZE=$(du -sh "${OUTPUT_DIR}" | cut -f1)

echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}构建完成!${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "离线部署包位置: ${YELLOW}${OUTPUT_DIR}${NC}"
echo -e "部署包大小: ${YELLOW}${TOTAL_SIZE}${NC}"
echo ""
echo -e "部署包内容:"
echo -e "  - langflow-offline.tar.gz   (Langflow 应用镜像)"
echo -e "  - postgres-16.tar.gz        (PostgreSQL 数据库镜像)"
echo -e "  - docker-compose.yml        (Docker Compose 配置)"
echo -e "  - deploy.sh                 (部署脚本)"
echo -e "  - README.md                 (部署说明)"
echo ""
echo -e "将整个 ${YELLOW}dist${NC} 目录复制到目标服务器即可进行离线部署。"
