# 台账管理系统

一个基于 Flask + Vue.js 3 的现代化台账管理系统，支持多用户、角色权限管理和完整的CRUD操作。

## 🚀 特性

- **用户管理**：支持用户注册、登录、角色管理
- **权限控制**：基于角色的访问控制（管理员、高级用户、普通用户）
- **台账管理**：完整的增删改查功能，支持搜索、筛选、排序
- **日志审计**：记录系统操作日志，管理员可查看
- **数据导出**：支持导出CSV格式数据
- **响应式设计**：适配不同屏幕尺寸

## 📋 技术栈

### 后端
- Python 3.6+
- Flask 2.3.3
- Flask-SQLAlchemy (ORM)
- Flask-JWT-Extended (认证)
- SQLite (数据库)

### 前端
- Vue.js 3.2
- Vue Router 4
- Pinia (状态管理)
- Element Plus (UI框架)
- Axios (HTTP客户端)

## 🛠️ 快速开始

### 环境要求

- Python 3.6 或更高版本
- Node.js 14 或更高版本
- npm 或 yarn

### 一键安装

#### Windows用户
```batch
# 下载项目后，在项目根目录运行
install.bat
```

#### Linux/Mac用户
```bash
# 下载项目后，在项目根目录运行
chmod +x install.sh
./install.sh
```

### 手动安装

1. **克隆项目**
   ```bash
   git clone <项目地址>
   cd ledger-management-system
   ```

2. **后端设置**
   ```bash
   cd backend
   python -m venv venv
   
   # Windows
   .\venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   
   pip install -r requirements.txt
   cp .env.example .env
   # 编辑 .env 文件，设置密钥
   ```

3. **前端设置**
   ```bash
   cd frontend
   npm install
   ```

### 配置

编辑 `backend/.env` 文件，修改以下配置：

```env
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here
ADMIN_PASSWORD=your-admin-password
```

### 运行项目

#### 使用启动脚本

Windows:
```batch
start.bat
```

Linux/Mac:
```bash
chmod +x start.sh
./start.sh
```

#### 手动运行

1. **启动后端**
   ```bash
   cd backend
   python run.py
   ```

2. **启动前端**
   ```bash
   cd frontend
   npm run serve
   ```

3. **访问系统**
   - 前端地址：http://localhost:8080
   - 后端API：http://localhost:5000/api

### 默认账号

- 管理员：admin / admin123

## 📁 项目结构

```
ledger-management-system/
├── backend/                 # 后端代码
│   ├── app/                # 应用模块
│   │   ├── api/           # API接口
│   │   ├── utils/         # 工具函数
│   │   ├── models.py      # 数据模型
│   │   ├── auth.py        # 认证模块
│   │   └── config.py      # 配置文件
│   ├── logs/              # 日志文件
│   ├── requirements.txt   # Python依赖
│   └── run.py            # 启动脚本
├── frontend/              # 前端代码
│   ├── public/           # 静态资源
│   ├── src/              # 源代码
│   │   ├── api/         # API封装
│   │   ├── router/      # 路由配置
│   │   ├── store/       # 状态管理
│   │   ├── utils/       # 工具函数
│   │   └── views/       # 页面组件
│   ├── package.json      # 依赖配置
│   └── vue.config.js     # Vue配置
└── README.md             # 项目说明
```

## 🔧 功能说明

### 用户角色

1. **管理员** (admin)
   - 查看所有台账
   - 编辑/删除所有台账
   - 查看系统日志
   - 管理用户

2. **高级用户** (power_user)
   - 查看所有台账
   - 编辑/删除所有台账
   - 无法查看系统日志

3. **普通用户** (user)
   - 只能查看自己的台账
   - 只能编辑/删除自己的台账

### 主要功能

- **台账管理**：创建、查看、编辑、删除台账记录
- **搜索过滤**：按关键词、省份、日期范围筛选
- **数据导出**：导出CSV格式的台账数据
- **系统日志**：记录用户操作，支持按级别、用户、时间筛选

## 🚀 生产部署

详细部署说明请查看 [部署和使用说明](./deployment-guide.md)

### 快速部署步骤

1. **构建前端**
   ```bash
   cd frontend
   npm run build
   ```

2. **配置Nginx**
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           root /path/to/frontend/dist;
           try_files $uri $uri/ /index.html;
       }
       
       location /api {
           proxy_pass http://localhost:5000;
       }
   }
   ```

3. **运行后端**
   ```bash
   cd backend
   gunicorn -w 4 -b 0.0.0.0:5000 wsgi:application
   ```

## ⚠️ 注意事项

1. **安全性**
   - 生产环境必须修改默认密钥和密码
   - 建议使用HTTPS
   - 定期备份数据库

2. **性能优化**
   - 大量数据时考虑使用MySQL或PostgreSQL
   - 配置缓存提高响应速度
   - 使用CDN加速静态资源

3. **维护建议**
   - 定期更新依赖包
   - 监控系统日志
   - 定期清理过期日志

## 📝 许可证

本项目采用 MIT 许可证

## 🤝 贡献

欢迎提交 Issue 和 Pull Request

## 📞 联系方式

如有问题，请提交 Issue 或联系项目维护者