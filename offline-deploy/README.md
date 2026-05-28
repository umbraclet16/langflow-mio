# Langflow 二次开发部署指南

## 概述

在已拉取 `langflowai/langflow:1.9.3` 官方镜像的基础上，构建包含二次开发代码的自定义镜像并部署到局域网。

## 文件说明

| 文件 | 说明 |
|------|------|
| `Dockerfile.deploy` | 基于官方镜像构建自定义镜像（核心文件） |
| `deploy/docker-compose.yml` | Docker Compose 部署配置（含 PostgreSQL） |
| `build-and-deploy.sh` | 一键构建镜像 + 启动服务 |
| `build.sh` | （旧方案）从零构建离线包 |
| `Dockerfile` | （旧方案）从零构建 Dockerfile |

## 使用方法

### 前置条件

1. 已拉取 `langflowai/langflow:1.9.3` 镜像
2. 在项目根目录下已修改完代码（二次开发）

### 方式一：一键构建部署

```bash
cd offline-deploy
./build-and-deploy.sh
```

等同于依次执行：
1. 在项目根目录执行 `docker build -f offline-deploy/Dockerfile.deploy -t langflow-custom:latest .`
2. 进入 `deploy/` 目录执行 `docker compose up -d`

### 方式二：仅构建镜像，手动启动

```bash
# 在项目根目录执行
docker build -t langflow-custom:latest -f offline-deploy/Dockerfile.deploy .
```

构建完成后可以：

**带 PostgreSQL 部署：**
```bash
cd offline-deploy/deploy
docker compose up -d
```

**仅用 SQLite 快速启动（无需 PostgreSQL）：**
```bash
docker run -d \
  --name langflow \
  -p 7860:7860 \
  -v langflow-data:/app/langflow \
  langflow-custom:latest
```

## Dockerfile.deploy 工作原理

分三个阶段：

| 阶段 | 基础镜像 | 做的事 |
|------|----------|--------|
| `backend` | `langflowai/langflow:1.9.3` | 复制项目源码 → `uv pip install --reinstall` 覆盖后端包 |
| `frontend-builder` | `langflowai/langflow:1.9.3` | `npm ci && npm run build` 重新构建前端 |
| `runtime` | 上一步的 `backend` | 合并前端构建产物到 site-packages |

### 如果只改了后端代码

注释掉 `Dockerfile.deploy` 中的前端构建阶段，构建更快：

```dockerfile
# FROM langflowai/langflow:1.9.3 AS frontend-builder
# ...
# COPY --from=frontend-builder ...
```

### 如果只改了前端代码

注释掉 `Dockerfile.deploy` 中的 backend 阶段的后端安装步骤，只跑前端构建。

## 配置

### 修改端口

编辑 `deploy/docker-compose.yml`:

```yaml
services:
  langflow:
    ports:
      - "8080:7860"  # 改为你想要的端口
```

### 修改数据库密码

编辑 `deploy/docker-compose.yml`:

```yaml
services:
  postgres:
    environment:
      POSTGRES_USER: 新用户名
      POSTGRES_PASSWORD: 新密码
  langflow:
    environment:
      - LANGFLOW_DATABASE_URL=postgresql://新用户名:新密码@postgres:5432/langflow
```

### 使用外部数据库

```yaml
services:
  langflow:
    environment:
      - LANGFLOW_DATABASE_URL=postgresql://用户:密码@数据库地址:5432/数据库名
    # depends_on 中移除 postgres
```

## 常用操作

### 查看日志

```bash
cd deploy && docker compose logs -f
docker compose logs -f langflow   # 只看 Langflow
docker compose logs -f postgres   # 只看数据库
```

### 停止 / 重启

```bash
cd deploy && docker compose down     # 停止
cd deploy && docker compose restart  # 重启
```

### 备份

```bash
# 备份数据库
docker exec langflow-postgres pg_dump -U langflow langflow > backup_$(date +%Y%m%d).sql

# 备份 Langflow 数据
docker run --rm -v langflow-data:/data -v $(pwd):/backup alpine tar czf /backup/langflow_data_$(date +%Y%m%d).tar.gz -C /data .
```
