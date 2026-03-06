# Docker 部署指南

本文档介绍如何使用 Docker 部署飞书 AI Bot（包括机器人服务和 Web 管理界面）。

## 镜像架构

Dockerfile 采用多阶段构建，优化镜像大小和构建效率：

### 阶段 1: 前端构建 (frontend-builder)
- 基础镜像：`node:20-alpine`
- 安装 npm 依赖
- 构建 Vue.js 前端应用
- 输出：编译后的静态文件

### 阶段 2: Python 依赖构建 (python-builder)
- 基础镜像：`python:3.11-slim`
- 安装编译工具（gcc, g++）
- 安装 Python 依赖到独立目录
- 输出：预编译的 Python 包

### 阶段 3: 最终运行镜像
- 基础镜像：`python:3.11-slim`
- 仅包含运行时依赖（curl）
- 复制前端构建产物和 Python 依赖
- 创建非 root 用户运行应用
- 最小化镜像大小

## 服务说明

容器运行 `python lark_bot.py`，会同时启动：
1. **飞书机器人服务** - 监听和处理飞书消息
2. **Web 管理界面** - 提供配置管理和提供商管理功能（默认端口 8080）

两个服务运行在同一个进程中，无需单独部署。

## 镜像大小优化

通过以下措施优化镜像大小：

1. **多阶段构建**：构建工具不包含在最终镜像中
2. **Alpine 基础镜像**：前端构建使用轻量级 Alpine
3. **精简依赖**：仅安装运行时必需的系统包
4. **清理缓存**：删除 apt 缓存和临时文件
5. **分离构建**：前端和后端依赖分别构建

预期镜像大小：约 500-600 MB（相比单阶段构建减少 30-40%）

## 构建镜像

### 从项目根目录构建

```bash
cd /path/to/lark-bot
docker build -f deployment/docker/Dockerfile -t feishu-bot:latest .
```

### 指定版本标签

```bash
docker build -f deployment/docker/Dockerfile -t feishu-bot:1.0.0 .
```

### 查看构建过程

```bash
docker build --progress=plain -f deployment/docker/Dockerfile -t feishu-bot:latest .
```

## 运行容器

### 基本运行

```bash
docker run -d \
  --name feishu-bot \
  -p 8080:8080 \
  -e FEISHU_APP_ID="your_app_id" \
  -e FEISHU_APP_SECRET="your_app_secret" \
  -e WEB_ADMIN_PASSWORD="your_secure_password" \
  -e JWT_SECRET_KEY="your_random_secret_key" \
  -e ENABLE_WEB_ADMIN=true \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  feishu-bot:latest
```

### 使用环境变量文件

创建 `.env` 文件（或使用项目根目录的 .env）：

```env
# 飞书应用配置（必需）
FEISHU_APP_ID=your_app_id
FEISHU_APP_SECRET=your_app_secret

# Web 管理界面配置
ENABLE_WEB_ADMIN=true
WEB_ADMIN_PORT=8080
WEB_ADMIN_HOST=0.0.0.0
WEB_ADMIN_PASSWORD=your_secure_password
JWT_SECRET_KEY=your_random_secret_key

# 其他配置
TARGET_PROJECT_DIR=/workspace
DEFAULT_CLI_PROVIDER=gemini
RESPONSE_LANGUAGE=zh-CN
```

运行容器：

```bash
docker run -d \
  --name feishu-bot \
  -p 8080:8080 \
  --env-file .env \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  feishu-bot:latest
```

## 环境变量

| 变量名 | 必需 | 默认值 | 说明 |
|--------|------|--------|------|
| `FEISHU_APP_ID` | 是 | - | 飞书应用 ID |
| `FEISHU_APP_SECRET` | 是 | - | 飞书应用密钥 |
| `WEB_ADMIN_PASSWORD` | 是 | - | 管理员登录密码 |
| `JWT_SECRET_KEY` | 是 | - | JWT 令牌签名密钥 |
| `WEB_ADMIN_PORT` | 否 | 8080 | Web 服务器监听端口 |
| `WEB_ADMIN_HOST` | 否 | 0.0.0.0 | Web 服务器监听地址 |
| `ENABLE_WEB_ADMIN` | 否 | true | 是否启用 Web 管理界面 |

## 数据持久化

容器使用以下目录存储数据，建议挂载为数据卷：

- `/app/data`：会话配置数据
- `/app/logs`：应用日志文件

### 创建数据卷

```bash
docker volume create feishu-bot-data
docker volume create feishu-bot-logs
```

### 使用数据卷运行

```bash
docker run -d \
  --name feishu-bot \
  -p 8080:8080 \
  -e FEISHU_APP_ID="your_app_id" \
  -e FEISHU_APP_SECRET="your_app_secret" \
  -e WEB_ADMIN_PASSWORD="your_secure_password" \
  -e JWT_SECRET_KEY="your_random_secret_key" \
  -v feishu-bot-data:/app/data \
  -v feishu-bot-logs:/app/logs \
  feishu-bot:latest
```

## 健康检查

容器内置健康检查，每 30 秒检查一次：

```bash
# 查看容器健康状态
docker ps

# 查看健康检查日志
docker inspect --format='{{json .State.Health}}' feishu-bot | jq
```

健康检查端点：`http://localhost:8080/api/health`

## 容器管理

### 查看日志

```bash
# 查看实时日志
docker logs -f feishu-bot

# 查看最近 100 行日志
docker logs --tail 100 feishu-bot
```

### 停止容器

```bash
docker stop feishu-bot
```

### 重启容器

```bash
docker restart feishu-bot
```

### 删除容器

```bash
docker rm -f feishu-bot
```

### 进入容器

```bash
docker exec -it feishu-bot /bin/bash
```

## 使用 Docker Compose

创建 `docker-compose.yml` 文件（参考 `deployment/docker/docker-compose.yml` 示例）：

```yaml
version: '3.8'

services:
  feishu-bot:
    build:
      context: ../..
      dockerfile: deployment/docker/Dockerfile
    container_name: feishu-bot
    ports:
      - "8080:8080"
    environment:
      - FEISHU_APP_ID=${FEISHU_APP_ID}
      - FEISHU_APP_SECRET=${FEISHU_APP_SECRET}
      - WEB_ADMIN_PASSWORD=${WEB_ADMIN_PASSWORD}
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s
```

### 启动服务

```bash
# 从 deployment/docker 目录运行
cd deployment/docker
docker-compose up -d

# 或从项目根目录运行
docker-compose -f deployment/docker/docker-compose.yml up -d
```

### 查看服务状态

```bash
docker-compose ps
```

### 查看日志

```bash
docker-compose logs -f feishu-bot
```

### 停止服务

```bash
docker-compose down
```

## 生产环境部署

### 使用 Nginx 反向代理

在宿主机上配置 Nginx：

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 配置 HTTPS

使用 Let's Encrypt 获取 SSL 证书：

```bash
certbot --nginx -d your-domain.com
```

### 资源限制

限制容器资源使用：

```bash
docker run -d \
  --name feishu-bot \
  --memory="1g" \
  --cpus="2.0" \
  -p 8080:8080 \
  -e FEISHU_APP_ID="your_app_id" \
  -e FEISHU_APP_SECRET="your_app_secret" \
  -e WEB_ADMIN_PASSWORD="your_secure_password" \
  -e JWT_SECRET_KEY="your_random_secret_key" \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  feishu-bot:latest
```

或在 docker-compose.yml 中：

```yaml
services:
  feishu-bot:
    # ... 其他配置 ...
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
```

## 故障排查

### 容器无法启动

1. 检查环境变量是否正确设置（特别是 FEISHU_APP_ID 和 FEISHU_APP_SECRET）
2. 查看容器日志：`docker logs feishu-bot`
3. 检查端口是否被占用：`netstat -tuln | grep 8080`

### 健康检查失败

1. 检查应用是否正常启动
2. 手动测试健康端点：`curl http://localhost:8080/api/health`
3. 查看应用日志

### 数据丢失

1. 确认数据卷正确挂载
2. 检查数据卷内容：`docker volume inspect feishu-bot-data`
3. 备份数据卷：`docker run --rm -v feishu-bot-data:/data -v $(pwd):/backup alpine tar czf /backup/data-backup.tar.gz /data`

### 前端无法访问

1. 检查前端构建是否成功
2. 验证静态文件是否存在：`docker exec feishu-bot ls -la /app/feishu_bot/web_admin/static`
3. 检查 Flask 静态文件配置

## 镜像优化建议

### 进一步减小镜像大小

1. 使用 `python:3.11-alpine` 作为最终镜像（需要额外配置）
2. 移除不必要的系统包
3. 使用 `.dockerignore` 排除更多文件

### 构建缓存优化

1. 将不常变化的层放在前面
2. 合理组织 COPY 指令
3. 使用 BuildKit 加速构建：`DOCKER_BUILDKIT=1 docker build .`

### 安全加固

1. 定期更新基础镜像
2. 扫描镜像漏洞：`docker scan feishu-bot:latest`
3. 使用非 root 用户运行（已实现）
4. 限制容器权限：`--read-only --tmpfs /tmp`

## 参考资源

- [Docker 官方文档](https://docs.docker.com/)
- [Docker Compose 文档](https://docs.docker.com/compose/)
- [多阶段构建最佳实践](https://docs.docker.com/build/building/multi-stage/)
- [Python Docker 最佳实践](https://docs.docker.com/language/python/build-images/)
