# 脚本目录

本目录包含项目的辅助脚本。

## 可用脚本

### 配置相关

- `setup_cron_token.py` - Cron API Token 自动配置脚本（推荐使用）
  
  **用途**: 自动配置 Cron API 的 JWT Token，让 AI Bot 能够创建和管理定时任务。
  
  **使用方法**:
  ```bash
  # 前提：Web Admin 服务正在运行
  python3 -m src.xagent.web_admin.server
  
  # 运行配置脚本
  python3 scripts/setup_cron_token.py
  ```
  
  **脚本功能**:
  - ✅ 检查 Web Admin 服务状态
  - ✅ 使用管理员密码登录获取 JWT Token
  - ✅ 将 Token 写入 `.env` 文件
  - ✅ 验证 Token 有效性
  
  **详细文档**: [Cron API 配置指南](../docs/guides/CRON_API_SETUP.md)

- `verify_config.py` - 验证配置文件格式和完整性

### 部署相关

- `deploy.sh` - 生产环境部署脚本
- `test_docker_build.sh` / `test_docker_build.ps1` - Docker 镜像构建测试脚本

### 配置验证

- `verify_config.py` - 验证配置文件格式和完整性
- `validate_nginx_config.sh` / `validate_nginx_config.ps1` - 验证 Nginx 配置文件

### 权限设置

- `set_file_permissions.py` - 设置文件权限（Linux/Unix）

## 启动服务

**注意**: 不再需要单独的启动脚本。

### 本地开发

直接运行主程序即可同时启动机器人和 Web 管理界面：

```bash
# Linux/Mac
python lark_bot.py

# Windows
python lark_bot.py
```

### Docker 部署

使用 Docker Compose：

```bash
cd deployment/docker
docker-compose up -d
```

详见 [Docker 部署指南](../deployment/docker/README.md)。

## 测试脚本

测试相关脚本位于 `scripts/test/` 目录。

## 已移除的脚本

以下脚本已被移除，因为功能已整合到主程序中：

- ~~`start_web_admin.sh`~~ - Web 管理界面现在随 `lark_bot.py` 一起启动
- ~~`start_all.sh`~~ - 不再需要分别启动多个服务
- ~~`start_all.bat`~~ - 不再需要分别启动多个服务
