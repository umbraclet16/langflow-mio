#!/bin/bash
# Langflow 离线部署 - 部署脚本
# 此脚本在目标服务器上运行，用于从离线包部署 Langflow

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}          Langflow 离线部署工具                               ${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
echo ""

# 检查 Docker 是否可用
if ! command -v docker &> /dev/null; then
    echo -e "${RED}错误: 未安装 Docker${NC}"
    echo "请先安装 Docker: https://docs.docker.com/engine/install/"
    exit 1
fi

# 检查 Docker Compose 是否可用
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo -e "${RED}错误: 未安装 Docker Compose${NC}"
    echo "请先安装 Docker Compose"
    exit 1
fi

# 检查必要的离线包文件
echo -e "${YELLOW}检查离线部署包...${NC}"

if [ ! -f "${SCRIPT_DIR}/langflow-offline.tar.gz" ]; then
    echo -e "${RED}错误: 未找到 langflow-offline.tar.gz${NC}"
    exit 1
fi

if [ ! -f "${SCRIPT_DIR}/postgres-16.tar.gz" ]; then
    echo -e "${RED}错误: 未找到 postgres-16.tar.gz${NC}"
    exit 1
fi

if [ ! -f "${SCRIPT_DIR}/docker-compose.yml" ]; then
    echo -e "${RED}错误: 未找到 docker-compose.yml${NC}"
    exit 1
fi

echo -e "${GREEN}✓ 离线部署包完整${NC}"

# 加载 Docker 镜像
echo ""
echo -e "${YELLOW}步骤 1/3: 加载 Docker 镜像...${NC}"

echo "正在加载 Langflow 镜像..."
docker load -i "${SCRIPT_DIR}/langflow-offline.tar.gz"

echo "正在加载 PostgreSQL 镜像..."
docker load -i "${SCRIPT_DIR}/postgres-16.tar.gz"

echo -e "${GREEN}✓ 镜像加载完成${NC}"

# 创建数据目录
echo ""
echo -e "${YELLOW}步骤 2/3: 创建数据目录...${NC}"

DATA_DIR="${SCRIPT_DIR}/data"
mkdir -p "${DATA_DIR}/langflow"
mkdir -p "${DATA_DIR}/postgres"

echo -e "${GREEN}✓ 数据目录已创建${NC}"

# 启动服务
echo ""
echo -e "${YELLOW}步骤 3/3: 启动服务...${NC}"

# 使用 docker-compose 启动
if command -v docker-compose &> /dev/null; then
    docker-compose -f "${SCRIPT_DIR}/docker-compose.yml" up -d
else
    docker compose -f "${SCRIPT_DIR}/docker-compose.yml" up -d
fi

echo -e "${GREEN}✓ 服务已启动${NC}"

# 等待服务就绪
echo ""
echo -e "${YELLOW}等待服务就绪...${NC}"

# 等待 PostgreSQL
echo -n "等待 PostgreSQL..."
for i in {1..30}; do
    if docker exec langflow-postgres pg_isready -U langflow &>/dev/null; then
        echo -e " ${GREEN}就绪${NC}"
        break
    fi
    echo -n "."
    sleep 2
done

# 等待 Langflow
echo -n "等待 Langflow..."
for i in {1..60}; do
    if curl -sf http://localhost:7860/health &>/dev/null; then
        echo -e " ${GREEN}就绪${NC}"
        break
    fi
    echo -n "."
    sleep 3
done

echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}部署完成!${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "访问地址: ${YELLOW}http://localhost:7860${NC}"
echo ""
echo -e "常用命令:"
echo -e "  查看日志:   docker-compose -f ${SCRIPT_DIR}/docker-compose.yml logs -f"
echo -e "  停止服务:   docker-compose -f ${SCRIPT_DIR}/docker-compose.yml down"
echo -e "  重启服务:   docker-compose -f ${SCRIPT_DIR}/docker-compose.yml restart"
echo ""
echo -e "数据目录: ${YELLOW}${DATA_DIR}${NC}"
