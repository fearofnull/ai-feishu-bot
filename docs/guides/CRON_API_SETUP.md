# Cron API 配置指南

本指南将帮助你配置 Cron API，让 AI Bot 能够创建和管理定时任务。

## 📋 目录

- [快速配置（推荐）](#快速配置推荐)
- [手动配置](#手动配置)
- [Token 有效期和刷新](#token-有效期和刷新)
- [常见问题](#常见问题)
- [安全建议](#安全建议)

---

## 🚀 快速配置（推荐）

我们提供了一个自动化脚本，可以一键完成所有配置步骤：

### 前提条件

1. **Web Admin 服务正在运行**

```bash
# 启动 Web Admin 服务
python3 -m src.xagent.web_admin.server
```

Web Admin 默认运行在 `http://localhost:8080`

**自定义端口**: 如果 Web Admin 运行在其他端口，使用命令行参数：

```bash
# 方式 1: 在 .env 中配置（持久化）
WEB_ADMIN_URL=http://localhost:YOUR_PORT

# 方式 2: 使用命令行参数（临时）
python3 scripts/setup_cron_token.py --url http://localhost:YOUR_PORT
```

2. **已安装 requests 库**

```bash
pip3 install requests
```

3. **（可选）配置 JWT 密钥**

JWT 密钥用于生成和验证 Token，建议在 `.env` 中设置：

```bash
# JWT 密钥（生产环境必须设置）
JWT_SECRET_KEY=your_secure_jwt_secret_key
```

**生成方法**：
- **使用 Python**：`python3 -c "import secrets; print(secrets.token_urlsafe(32))"`
- **使用 OpenSSL**：`openssl rand -hex 32`
- **使用在线工具**：搜索 "random secret generator"

**建议**：使用 32 字符以上的随机字符串，包含大小写字母、数字和符号

### 使用自动化脚本

```bash
# 基本用法（使用默认配置）
python3 scripts/setup_cron_token.py

# 指定 Web Admin 地址
python3 scripts/setup_cron_token.py --url http://localhost:9090

# 指定管理员密码
python3 scripts/setup_cron_token.py --password mypassword

# 指定 Token 有效期（小时）
python3 scripts/setup_cron_token.py --expiry 4

# 完整配置
python3 scripts/setup_cron_token.py --url http://localhost:9090 --password mypassword --expiry 4
```

脚本会自动完成以下操作：

✅ 检查 Web Admin 服务状态  
✅ 使用管理员密码登录  
✅ 获取 JWT Token  
✅ 将 Token 写入 `.env` 文件  
✅ 验证 Token 有效性  

**注意**:
- 命令行参数优先级高于 `.env` 配置
- `--url`、`--password`、`--expiry` 都是可选的
- 未指定的参数会从 `.env` 读取或使用默认值

### 脚本输出示例

```
============================================================
Cron API Token 配置工具
============================================================

📁 配置文件: /Users/xxx/lark-bot/.env

🌐 Web Admin 地址: http://localhost:8080
🔍 检查 Web Admin 服务状态...
✅ Web Admin 服务运行正常

🔑 管理员密码: ***（使用默认 admin123）
🔐 正在登录 Web Admin...
✅ 登录成功！
📋 Token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...3dY

🔍 验证 Token 有效性...
✅ Token 验证成功！

💾 已保存 Token 到 .env 文件

============================================================
✅ 配置完成！
============================================================

📝 重要提示:
   • Token 有效期为 2 小时
   • 过期后需要重新运行此脚本
   • 建议定期更换管理员密码

🚀 现在可以重启应用使用 Cron API 功能了:
   python3 main.py
```

---

## 🔧 手动配置

如果你不想使用自动化脚本，可以手动完成配置：

### 步骤 1：设置管理员密码

在 `.env` 文件中添加（或修改）：

```bash
# Web Admin 管理员密码
WEB_ADMIN_PASSWORD=your_secure_password_here
```

**默认密码**: `admin123`（仅用于开发环境）

### 步骤 2：启动 Web Admin 服务

```bash
python3 -m src.xagent.web_admin.server
```

### 步骤 3：获取 JWT Token

使用 `curl` 或其他 HTTP 客户端登录：

```bash
curl -X POST http://localhost:8080/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"password": "your_secure_password_here"}'
```

**成功响应示例**：

```json
{
  "success": true,
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expires_in": 7200,
    "expires_at": "2024-01-01T14:00:00"
  },
  "message": "Login successful"
}
```

### 步骤 4：配置 Token

将获取到的 `token` 值添加到 `.env` 文件：

```bash
# Web Admin 配置
WEB_ADMIN_URL=http://localhost:8080
WEB_ADMIN_TOKEN=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### 步骤 5：重启应用

```bash
# 停止当前运行的应用
# 然后重新启动
python3 main.py
```

---

## ⏰ Token 有效期和刷新

### 有效期

- **默认有效期**: 2 小时（7200 秒）
- **过期行为**: Token 失效后，Cron API 调用会返回 `401 UNAUTHORIZED`
- **配置方式**: 使用脚本参数 `--expiry` 指定有效期（单位：小时）

### 刷新 Token

当 Token 过期后，有两种方式刷新：

#### 方式 1：使用自动化脚本（推荐）

```bash
# 重新运行配置脚本
python3 scripts/setup_cron_token.py

# 指定新的有效期
python3 scripts/setup_cron_token.py --expiry 8
```

#### 方式 2：手动刷新

重复[手动配置](#手动配置)的步骤 3-5

### 有效期说明

Token 有效期由 Web Admin 服务端控制，默认为 2 小时。这是安全机制，防止长期有效的 Token 被滥用。

**建议**:
- 开发环境：可以使用较长的有效期（4-8 小时）
- 生产环境：建议使用默认 2 小时
- 高安全要求：可以使用 1 小时

---

## ❓ 常见问题

### Q1: 为什么需要配置 Token？

**A**: Cron API 是 Web Admin 提供的受保护接口，需要身份验证才能访问。Token 是 JWT（JSON Web Token），用于证明调用者的身份。

### Q2: Token 过期了怎么办？

**A**: Token 有效期为 2 小时，过期后重新运行配置脚本即可：

```bash
python3 scripts/setup_cron_token.py
```

### Q3: 如何修改管理员密码？

**A**: 在 `.env` 文件中修改 `WEB_ADMIN_PASSWORD`，然后重启 Web Admin 服务：

```bash
# 修改 .env
WEB_ADMIN_PASSWORD=new_secure_password

# 重启 Web Admin
python3 -m src.xagent.web_admin.server
```

### Q4: Web Admin 服务没有运行怎么办？

**A**: 按照以下步骤启动：

```bash
# 1. 检查端口是否被占用
lsof -i :8080

# 2. 如果被占用，停止占用进程或更换端口
# 3. 启动 Web Admin
python3 -m src.xagent.web_admin.server
```

### Q5: 如何验证配置是否成功？

**A**: 运行配置脚本时，它会自动验证 Token。你也可以手动测试：

```bash
# 测试 Cron API
curl http://localhost:8080/api/cron/jobs \
  -H "Authorization: Bearer YOUR_TOKEN"
```

如果返回 JSON 数据（不是 401 错误），说明配置成功。

### Q6: 可以在多个环境使用同一个 Token 吗？

**A**: 不可以。每个 Token 绑定到特定的 Web Admin 实例。如果你有多个环境（开发、测试、生产），需要分别为每个环境配置。

---

## 🔒 安全建议

### 1. 不要使用默认密码

**生产环境** 必须修改默认密码：

```bash
# 在 .env 中设置强密码
WEB_ADMIN_PASSWORD=your_very_secure_password_here
```

### 2. 保护 .env 文件

```bash
# 设置文件权限（仅所有者可读写）
chmod 600 .env

# 不要提交到版本控制
echo ".env" >> .gitignore
```

### 3. 定期更换密码

建议每 3-6 个月更换一次管理员密码：

```bash
# 1. 生成新密码
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# 2. 更新 .env 中的 WEB_ADMIN_PASSWORD

# 3. 重启 Web Admin 服务

# 4. 重新配置 Token
python3 scripts/setup_cron_token.py
```

### 4. 监控异常登录

Web Admin 会记录所有登录尝试，包括失败的尝试。定期检查日志：

```bash
# 查看登录日志
tail -f logs/web_admin.log | grep "authentication"
```

### 5. 使用 HTTPS（生产环境）

在生产环境中，建议使用 HTTPS：

```bash
# 在 .env 中配置
WEB_ADMIN_URL=https://your-domain.com
```

---

## 📚 相关文档

- [Web 管理界面用户指南](./WEB_ADMIN_USER_GUIDE.md)
- [部署指南](../deployment/DEPLOYMENT.md)
- [API 文档](../guides/API_DOCUMENTATION.md)

---

## 🆘 获取帮助

如果遇到问题：

1. 检查 [常见问题](#常见问题) 部分
2. 查看 Web Admin 日志：`logs/web_admin.log`
3. 查看 Bot 日志：`logs/xagent.log`
4. 提交 Issue 到项目仓库

---

**最后更新**: 2026-03-22  
**维护者**: Lark Bot Team