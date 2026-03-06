# Web 管理界面前端

基于 Vue 3 + Element Plus 的 Web 管理界面。

## 技术栈

- **Vue 3**: 渐进式 JavaScript 框架
- **Element Plus**: 企业级 UI 组件库
- **Vite**: 快速构建工具
- **Pinia**: 状态管理
- **Vue Router**: 路由管理
- **Axios**: HTTP 客户端

## 开发

### 安装依赖

```bash
npm install
```

### 开发模式

启动开发服务器（热重载）：

```bash
npm run dev
```

访问 `http://localhost:5173`

**注意**: 开发模式下需要后端服务运行在 `http://localhost:8080`

### 构建生产版本

```bash
npm run build
```

构建产物会输出到 `dist/` 目录，并自动复制到 `../feishu_bot/web_admin/static/`

### 预览生产构建

```bash
npm run preview
```

## 项目结构

```
frontend/
├── public/              # 静态资源
├── src/
│   ├── api/            # API 接口
│   ├── assets/         # 资源文件
│   ├── components/     # 组件
│   ├── router/         # 路由配置
│   ├── stores/         # Pinia 状态管理
│   ├── views/          # 页面视图
│   ├── App.vue         # 根组件
│   └── main.js         # 入口文件
├── index.html          # HTML 模板
├── vite.config.js      # Vite 配置
└── package.json        # 依赖配置
```

## 配置

### API 基础 URL

开发环境和生产环境的 API 地址在 `src/api/client.js` 中配置：

```javascript
const API_BASE_URL = import.meta.env.DEV 
  ? 'http://localhost:8080'  // 开发环境
  : '';                       // 生产环境（相对路径）
```

### 代理配置

开发模式下的代理配置在 `vite.config.js` 中：

```javascript
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8080',
      changeOrigin: true
    }
  }
}
```

## 构建优化

- **代码分割**: 自动分割 vendor 和业务代码
- **Gzip 压缩**: 生成 `.gz` 和 `.br` 压缩文件
- **Tree Shaking**: 自动移除未使用的代码
- **资源优化**: 图片和字体自动优化

## 常见问题

### 开发模式下 API 请求失败

确保后端服务运行在 `http://localhost:8080`：

```bash
# 在项目根目录
python lark_bot.py
```

### 构建后静态文件路径错误

检查 `vite.config.js` 中的 `base` 配置：

```javascript
export default defineConfig({
  base: '/',  // 生产环境的基础路径
  // ...
})
```

### 热重载不工作

1. 检查 Vite 开发服务器是否正常运行
2. 清除浏览器缓存
3. 重启开发服务器

## 部署

### 本地部署

构建后直接运行后端服务：

```bash
npm run build
cd ..
python lark_bot.py
```

访问 `http://localhost:8080`

### Docker 部署

Docker 构建会自动构建前端，无需手动操作：

```bash
cd deployment/docker
docker-compose up -d
```

## 开发规范

### 代码风格

- 使用 2 空格缩进
- 使用单引号
- 组件名使用 PascalCase
- 文件名使用 kebab-case

### 提交规范

遵循 Conventional Commits：

- `feat`: 新功能
- `fix`: 修复 bug
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建/工具相关

## 相关文档

- [Vue 3 文档](https://vuejs.org/)
- [Element Plus 文档](https://element-plus.org/)
- [Vite 文档](https://vitejs.dev/)
- [Pinia 文档](https://pinia.vuejs.org/)
