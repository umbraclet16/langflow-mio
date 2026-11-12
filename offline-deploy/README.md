# Langflow 二次开发离线部署指南

## 概述

在 `langflowai/langflow:1.9.3` 官方镜像的基础上,通过 `Dockerfile` 把二次开发代码(后端包 + 前端构建产物)打进自定义镜像 `langflow-custom:latest`,用于局域网/离线部署。

开发与部署使用不同的 compose 形态,**代码进入容器的方式**是两者的本质区别:

| | 开发形态(`dev/`) | 部署形态(`deploy/`) |
|------|------------------|---------------------|
| 镜像 | 官方 `langflowai/langflow:1.9.3` | 二开镜像 `langflow-custom:latest` |
| 代码进入方式 | volume 挂载本地源码进容器 site-packages | 构建时由 Dockerfile 打进镜像 |
| 改代码后 | 重启容器即生效 | 需重新 build 镜像 |
| 适用场景 | 本机开发调试 | 部署到其他服务器 / 长期运行 |

## 目录结构

```
offline-deploy/
├── README.md            # 本文件
├── Dockerfile           # 基于官方镜像构建二开镜像(核心文件)
├── build-and-deploy.sh  # 一键:构建镜像 + 启动 deploy/
├── dev/                 # 开发形态
│   ├── docker-compose.yml   # 官方镜像 + 源码挂载
│   ├── .env                 # 环境变量(不入库)
│   └── .env.example         # 环境变量模板
└── deploy/              # 部署形态
    ├── docker-compose.yml   # 二开镜像,无源码挂载
    ├── .env
    └── .env.example
```

> `.env` 已被根目录 `.gitignore` 忽略,首次使用时从 `.env.example` 复制并按需修改(当前主要是 `AGENT_PLATFORM_API_URL`)。

## 开发模式(dev/)

```bash
cd offline-deploy/dev
docker compose up -d
# 访问 http://localhost:7860
```

- 使用官方镜像,把本仓库的 `src/backend/base/langflow/`、`src/lfx/`、`src/frontend/build/`、`mcp-scripts/` 挂载进容器的 site-packages / 对应路径
- **前置条件**:`src/frontend/build/` 需存在(在仓库根目录跑过 `make frontend` 或 `npm run build`)
- 改后端/前端代码后 `docker compose restart langflow` 即生效,无需重建镜像

## 部署模式(deploy/)

前置条件:
- 宿主机已有 `src/frontend/build/`(构建镜像**不执行 npm**,直接使用该产物;没有则先在仓库根目录 `make frontend`)
- 本机已有基础镜像 `langflowai/langflow:1.9.3`(离线环境先 `docker load` 导入)

### 方式一:一键构建部署

```bash
cd offline-deploy
./build-and-deploy.sh
```

等同于:
1. 在项目根目录 `docker build -f offline-deploy/Dockerfile -t langflow-custom:latest .`
2. `cd deploy && docker compose up -d`

### 方式二:手动构建 + 启动

```bash
# 在项目根目录执行
docker build -t langflow-custom:latest -f offline-deploy/Dockerfile .

cd offline-deploy/deploy
docker compose up -d
```

### 离线分发到其他服务器

两条路径:

1. **在有网机器构建好再分发**(推荐):构建 `langflow-custom:latest` 后导出 tar 拷过去
2. **在离线机上打镜像**:先把官方基础镜像 `langflowai/langflow:1.9.3` 的 tar 拷到离线机 `docker load`,再按上面的"部署模式"正常 `docker build`——构建本身不联网(不执行 npm/uv)

```bash
# 有网机器上导出镜像
docker save langflow-custom:latest | gzip > langflow-custom.tar.gz
# 或导出基础镜像,供离线机自行构建
docker save langflowai/langflow:1.9.3 | gzip > langflow-1.9.3.tar.gz
# postgres 镜像同理(目标机没有时)
docker save postgres:16-bookworm | gzip > postgres-16.tar.gz

# 拷贝 tar.gz 与整个 offline-deploy/deploy/ 目录到目标机
# 目标机上:
docker load -i langflow-custom.tar.gz      # 或先 load 基础镜像再构建
docker load -i postgres-16.tar.gz
cd deploy && docker compose up -d
```

### 仅用 SQLite 快速启动(无需 PostgreSQL)

```bash
docker run -d --name langflow -p 7860:7860 -v langflow-data:/app/langflow langflow-custom:latest
```

## Dockerfile 工作原理

以官方镜像为底做**覆盖式替换**,不执行任何 npm / uv 命令,构建全程无需网络(仅要求基础镜像已在本地):

| 步骤 | 做的事 |
|------|--------|
| 1 | 删除镜像自带的 `langflow` / `lfx` / `langflow_sdk` 包代码(避免残留已删除的旧文件) |
| 2 | `COPY` 仓库源码进 site-packages,目录与 `dev/` 的挂载一一对应 |
| 3 | 用宿主机 `src/frontend/build/` 整体替换包内前端产物(仓库源码里的 `langflow/frontend` 是旧产物) |

改代码后的操作:
- 只改后端:直接重新 `docker build`
- 只改前端:先在仓库根目录 `make frontend` 更新 `src/frontend/build/`,再重新 `docker build`

> 仓库根目录执行 `docker build` 时,`offline-deploy/Dockerfile.dockerignore` 会精简构建上下文(排除 `.git`、`node_modules` 等),只对该 Dockerfile 生效。

> 版本元数据(`dist-info`)仍是官方 1.9.3,与 dev 挂载形态行为一致。若二次开发引入了**新的第三方依赖**,需另行安装(两种形态都如此)。

## 配置

### 环境变量

两个 compose 共用的关键变量(详见文件内注释):

- `AGENT_PLATFORM_API_URL`:Agent Platform API 地址,从同目录 `.env` 读取
- `LANGFLOW_MCP_SERVER_SOURCE` / `MCP_SERVER_WORKDIR`:MCP 工具来源与 stdio 脚本工作目录
- `LANGFLOW_CREATE_STARTER_PROJECTS` / `LANGFLOW_UPDATE_STARTER_PROJECTS`:Starter Projects 的创建/更新开关
- `LANGFLOW_AUTO_LOGIN` + `LANGFLOW_SKIP_AUTH_AUTO_LOGIN`:免登录(如需正常登录流程改为 `false` 并去掉 SKIP)

> 部署形态默认无 `mcp-scripts` 挂载;若部署机上要用 stdio MCP 服务,把脚本目录放到 `MCP_SERVER_WORKDIR` 对应路径并启用 `deploy/docker-compose.yml` 中被注释的挂载。

### 修改端口

编辑对应 `docker-compose.yml`:

```yaml
services:
  langflow:
    ports:
      - "8080:7860"  # 改为你想要的端口
```

### 修改数据库密码

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
    # depends_on 中移除 postgres,并删除 postgres 服务
```

## 常用操作

```bash
cd offline-deploy/dev    # 或 deploy
docker compose logs -f             # 全部日志
docker compose logs -f langflow    # 只看 Langflow
docker compose logs -f postgres    # 只看数据库
docker compose down                # 停止
docker compose restart             # 重启
```

## 备份

```bash
# 备份数据库
docker exec langflow-postgres pg_dump -U langflow langflow > backup_$(date +%Y%m%d).sql

# 备份 Langflow 数据
docker run --rm -v langflow-data:/data -v $(pwd):/backup alpine tar czf /backup/langflow_data_$(date +%Y%m%d).tar.gz -C /data .
```
