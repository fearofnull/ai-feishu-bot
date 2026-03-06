# Docker 快速部署指南

5分钟快速部署飞书AI机器人到云端服务器。

## 前置要求

- 一台云服务器（推荐配置：2核4GB，Ubuntu 20.04+）
- Docker 和 Docker Compose 已安装
- 飞书应用凭证
- 至少一个AI API密钥

## 快速部署

### 1. 安装 Docker（如果未安装）

```bash
# 安装 Docker
curl -fsSL https://get.docker.com | sh

# 启动 Docker
sudo systemctl start docker
sudo systemctl enable docker

# 添加当前用户到 docker 组（可选，避免每次使用 sudo）
sudo usermod -aG docker $USER
newgrp docker

# 安装 Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 验证安装
docker --version
docker-compose --version
```

### 2. 克隆项目

```bash
git clone <repository-url>
cd feishu-ai-bot
```

### 3. 配置环境变量

```bash
# 复制配置模板
cp .env.example .env

# 编辑配置（使用 nano 或 vim）
nano .env
```

**必需配置**（至少填写这些）：
```bash
# 飞书应用配置
FEISHU_APP_ID=your_app_id_here
FEISHU_APP_SECRET=your_app_secret_here

# AI API 配置（至少配置一个）
CLAUDE_API_KEY=your_claude_api_key
# 或
GEMINI_API_KEY=your_gemini_api_key
# 或
OPENAI_API_KEY=your_openai_api_key

# 语言配置（可选）
RESPONSE_LANGUAGE=zh-CN  # 设置为中文
```

保存并退出（Ctrl+X，然后 Y，然后 Enter）。

### 4. 启动服务

```bash
# 使用 Docker Compose（推荐）
docker-compose up -d

# 或使用部署脚本
chmod +x deploy.sh
./deploy.sh start
```

### 5. 查看日志

```bash
# 实时查看日志
docker-compose logs -f

# 或使用部署脚本
./deploy.sh logs
```

看到类似以下输出说明启动成功：
```
✅ Configuration loaded successfully
✅ FeishuBot initialized successfully
✅ Scheduler started
Starting FeishuBot...
```

## 常用命令

```bash
# 查看服务状态
docker-compose ps
# 或
./deploy.sh status

# 停止服务
docker-compose down
# 或
./deploy.sh stop

# 重启服务
docker-compose restart
# 或
./deploy.sh restart

# 更新服务（拉取最新代码并重新部署）
git pull
docker-compose up -d --build
# 或
./deploy.sh update

# 备份数据
./deploy.sh backup
```

## 验证部署

1. 在飞书中找到你的机器人
2. 在群聊中 @机器人 发送消息："你好"
3. 机器人应该会回复

如果没有回复，检查日志：
```bash
docker-compose logs -f
```

## 故障排除

### 问题1：容器启动失败

```bash
# 查看详细日志
docker-compose logs

# 检查配置
cat .env

# 验证配置
docker run --rm --env-file .env feishu-ai-bot python config.py
```

### 问题2：机器人无响应

1. 检查飞书应用配置是否正确
2. 检查网络连接
3. 查看日志中的错误信息

```bash
docker-compose logs -f | grep ERROR
```

### 问题3：内存不足

调整 `docker-compose.yml` 中的资源限制：

```yaml
deploy:
  resources:
    limits:
      memory: 1G  # 降低内存限制
```

## 安全建议

1. **保护 .env 文件**
```bash
chmod 600 .env
```

2. **配置防火墙**（如果需要）
```bash
# 只允许必要的端口
sudo ufw allow 22/tcp  # SSH
sudo ufw enable
```

3. **定期备份**
```bash
# 添加到 crontab
crontab -e

# 每天凌晨2点备份
0 2 * * * cd /path/to/feishu-ai-bot && ./deploy.sh backup
```

4. **定期更新**
```bash
# 每周检查更新
git pull
docker-compose up -d --build
```

## 监控和维护

### 查看资源使用

```bash
# 实时监控
docker stats feishu-ai-bot

# 查看磁盘使用
df -h
du -sh data/
```

### 清理日志

```bash
# Docker 会自动轮转日志（配置在 docker-compose.yml 中）
# 手动清理旧日志
docker-compose logs --tail=0 > /dev/null
```

### 查看会话数据

```bash
# 查看会话文件
ls -lh data/

# 查看会话内容（JSON 格式）
cat data/sessions.json | python -m json.tool
```

## 高级配置

### 使用自定义域名（可选）

如果需要 webhook 功能，可以配置 Nginx 反向代理：

```bash
# 安装 Nginx
sudo apt-get install nginx

# 配置反向代理
sudo nano /etc/nginx/sites-available/feishu-bot

# 添加配置
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

# 启用配置
sudo ln -s /etc/nginx/sites-available/feishu-bot /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 配置 HTTPS（推荐）

```bash
# 安装 Certbot
sudo apt-get install certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d your-domain.com

# 自动续期
sudo certbot renew --dry-run
```

## 性能优化

### 1. 调整资源限制

根据实际使用情况调整 `docker-compose.yml`：

```yaml
deploy:
  resources:
    limits:
      cpus: '1'      # 降低 CPU 限制
      memory: 1G     # 降低内存限制
```

### 2. 优化会话配置

在 `.env` 中调整：

```bash
MAX_SESSION_MESSAGES=30  # 减少会话历史
CACHE_SIZE=500           # 减少缓存大小
```

### 3. 使用 SSD 存储

确保 `data/` 目录在 SSD 上，提高读写性能。

## 下一步

- 阅读 [完整部署文档](DEPLOYMENT.md)
- 了解 [配置选项](../CONFIGURATION.md)
- 查看 [使用示例](../../README.md#使用示例)

## 获取帮助

如果遇到问题，请查看日志文件或提交 GitHub Issue。

---

**祝你部署顺利！** 🚀
