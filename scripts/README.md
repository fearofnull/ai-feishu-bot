# 脚本目录

本目录包含项目的辅助脚本。

## 可用脚本

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
