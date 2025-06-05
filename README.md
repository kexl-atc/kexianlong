# 台账管理系统 - 快速参考指南

## 🚀 快速开始（5分钟）

### 1. 下载项目
```bash
# 下载项目文件到本地
# 解压到 ledger-management-system 目录
```

### 2. 一键安装
**Windows:**
```batch
cd ledger-management-system
install.bat
```

**Linux/Mac:**
```bash
cd ledger-management-system
chmod +x install.sh
./install.sh
```

### 3. 配置密钥
编辑 `backend/.env` 文件：
```env
SECRET_KEY=your-very-long-random-string-here
JWT_SECRET_KEY=another-very-long-random-string
ADMIN_PASSWORD=your-secure-admin-password
```

### 4. 启动系统
**Windows:**
```batch
start.bat
```

**Linux/Mac:**
```bash
./start.sh
```

### 5. 访问系统
- 打开浏览器访问：http://localhost:8080
- 默认账号：admin / change_this_password

## 📁 核心文件说明

### 必须修改的文件
1. `backend/.env` - 环境配置（密钥、密码）
2. `frontend/.env.production` - 生产环境API地址

### 重要配置文件
- `backend/app/config.py` - 后端配置
- `frontend/vue.config.js` - 前端构建配置
- `backend/requirements.txt` - Python依赖
- `frontend/package.json` - Node.js依赖

### 数据库文件
- `backend/ledger.db` - SQLite数据库（自动创建）
- `backend/backups/` - 数据库备份目录

## 🔑 默认角色权限

| 角色 | 查看自己数据 | 查看所有数据 | 编辑/删除自己数据 | 编辑/删除所有数据 | 系统管理 |
|------|------------|------------|----------------|----------------|---------|
| 普通用户 | ✓ | ✗ | ✓ | ✗ | ✗ |
| 高级用户 | ✓ | ✓ | ✓ | ✓ | ✗ |
| 管理员 | ✓ | ✓ | ✓ | ✓ | ✓ |

## 📝 常用命令

### 后端命令
```bash
# 创建用户
flask create-user username password --role admin

# 初始化数据库
flask init-db

# 重置数据库（危险）
flask reset-db

# 填充测试数据
flask seed-data
```

### 数据库备份
```bash
# Windows
cd backend/scripts
backup.bat

# Linux/Mac
cd backend/scripts
./backup.sh
```

### 健康检查
```bash
cd backend/scripts
python health_check.py
```

## 🔧 常见问题快速解决

### 1. 端口被占用
**问题**：`Error: Port 5000/8080 is already in use`

**解决**：
```bash
# Windows - 查找并结束进程
netstat -ano | findstr :5000
taskkill /PID <进程ID> /F

# Linux/Mac
lsof -i :5000
kill -9 <进程ID>
```

### 2. 依赖安装失败
**问题**：`pip install` 或 `npm install` 失败

**解决**：
```bash
# 使用国内镜像
# Python
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# Node.js
npm install --registry https://registry.npm.taobao.org
```

### 3. 数据库锁定
**问题**：`database is locked`

**解决**：
1. 关闭所有访问数据库的程序
2. 删除临时文件：`rm backend/ledger.db-journal`
3. 重启后端服务

### 4. 登录一直失败
**问题**：用户名密码正确但无法登录

**检查步骤**：
1. 确认后端服务正在运行
2. 检查浏览器控制台网络请求
3. 查看后端日志：`backend/logs/app.log`
4. 确认JWT密钥已配置

## 📊 API快速测试

使用curl测试API：

```bash
# 登录获取Token
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# 使用Token访问API
TOKEN="your-token-here"
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:5000/api/ledger
```

## 🚢 生产部署清单

- [ ] 修改所有默认密钥和密码
- [ ] 配置HTTPS证书
- [ ] 设置防火墙规则
- [ ] 配置自动备份
- [ ] 设置日志轮转
- [ ] 配置监控告警
- [ ] 压力测试
- [ ] 制定应急预案

## 📞 获取帮助

1. **查看日志**
   - 后端日志：`backend/logs/app.log`
   - 健康检查日志：`backend/logs/health_check.log`

2. **调试模式**
   - 后端：`FLASK_DEBUG=True`
   - 前端：浏览器开发者工具（F12）

3. **性能分析**
   ```bash
   cd backend/scripts
   python performance_monitor.py
   ```

## 🎯 下一步

1. **基础使用**
   - 创建第一个台账记录
   - 尝试搜索和筛选功能
   - 导出数据测试

2. **进阶配置**
   - 修改省份列表
   - 自定义性质选项
   - 配置邮件通知

3. **系统扩展**
   - 添加新的API接口
   - 自定义前端组件
   - 集成第三方服务

---

💡 **提示**：遇到问题时，先查看相关日志文件，大部分问题都能从日志中找到原因。

📌 **记住**：生产环境部署前，一定要修改所有默认配置！

# 台账管理系统部署和使用说明

## 项目概述

这是一个基于 Flask (后端) 和 Vue.js 3 (前端) 的台账管理系统，具有以下主要功能：

- 用户认证和角色管理（管理员、高级用户、普通用户）
- 台账的增删改查功能
- 基于角色的权限控制
- 系统日志记录和查看
- 数据导出功能

## 文件结构

项目包含以下文件数量：

### 后端文件 (17个文件)
```
backend/
├── app/
│   ├── __init__.py          # 应用初始化
│   ├── models.py            # 数据模型
│   ├── auth.py              # 认证模块
│   ├── config.py            # 配置文件
│   ├── api/
│   │   ├── __init__.py      # API包初始化
│   │   ├── ledger.py        # 台账API
│   │   ├── admin.py         # 管理员API
│   │   └── meta.py          # 元数据API
│   └── utils/
│       ├── __init__.py      # 工具包初始化
│       └── decorators.py    # 装饰器工具
├── requirements.txt         # Python依赖
├── run.py                   # 运行脚本
├── wsgi.py                  # WSGI入口
├── .env.example             # 环境变量示例
└── logs/                    # 日志目录（自动创建）
```

### 前端文件 (23个文件)
```
frontend/
├── public/
│   └── index.html           # HTML模板
├── src/
│   ├── api/
│   │   ├── auth.js          # 认证API
│   │   ├── ledger.js        # 台账API
│   │   └── admin.js         # 管理员API
│   ├── router/
│   │   └── index.js         # 路由配置
│   ├── store/
│   │   └── user.js          # 用户状态管理
│   ├── utils/
│   │   └── request.js       # 请求工具
│   ├── views/
│   │   ├── LoginPage.vue    # 登录页面
│   │   ├── LedgerList.vue   # 台账列表
│   │   ├── LedgerForm.vue   # 台账表单
│   │   ├── AdminLogView.vue # 管理员日志
│   │   └── NotFound.vue     # 404页面
│   ├── App.vue              # 主组件
│   └── main.js              # 入口文件
├── .env.development         # 开发环境配置
├── .env.production          # 生产环境配置
├── package.json             # 依赖配置
└── vue.config.js            # Vue配置
```

总计：40个文件

## 本地开发环境设置

### 前置要求

1. **Python 3.6+**
   - 下载地址: https://www.python.org/downloads/
   - 安装时勾选 "Add Python to PATH"

2. **Node.js 14+**
   - 下载地址: https://nodejs.org/
   - 推荐安装 LTS 版本

### 后端设置

1. **进入后端目录**
   ```bash
   cd backend
   ```

2. **创建虚拟环境**
   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate

   # Mac/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

4. **配置环境变量**
   ```bash
   # 复制环境变量示例文件
   cp .env.example .env
   
   # 编辑 .env 文件，修改以下配置：
   # SECRET_KEY=your-secret-key
   # JWT_SECRET_KEY=your-jwt-secret-key
   # ADMIN_PASSWORD=your-admin-password
   ```

5. **初始化数据库**
   ```bash
   # 创建数据库表
   flask init-db
   
   # 创建管理员用户（可选，默认会自动创建admin/admin123）
   flask create-user admin newpassword --role admin
   ```

6. **运行后端服务**
   ```bash
   # 开发模式
   python run.py
   
   # 或使用 Flask 命令
   flask run --debug --port 5000
   ```

   后端将在 http://localhost:5000 运行

### 前端设置

1. **进入前端目录**
   ```bash
   cd frontend
   ```

2. **安装依赖**
   ```bash
   npm install
   # 或使用 yarn
   yarn install
   ```

3. **运行开发服务器**
   ```bash
   npm run serve
   # 或使用 yarn
   yarn run serve
   ```

   前端将在 http://localhost:8080 运行

### 默认账号

- 管理员账号：admin / admin123（首次登录请修改密码）

## 生产环境部署

### 后端部署（使用Gunicorn）

1. **安装额外依赖**
   ```bash
   pip install gunicorn
   ```

2. **设置生产环境变量**
   ```bash
   export FLASK_ENV=production
   export SECRET_KEY=your-production-secret-key
   export JWT_SECRET_KEY=your-production-jwt-key
   ```

3. **运行Gunicorn**
   ```bash
   gunicorn -w 4 -b 0.0.0.0:5000 wsgi:application
   ```

### 前端部署

1. **修改生产环境配置**
   编辑 `.env.production` 文件：
   ```
   VUE_APP_API_BASE_URL=http://your-server-domain.com/api
   ```

2. **构建生产版本**
   ```bash
   npm run build
   # 或使用 yarn
   yarn build
   ```

3. **部署dist目录**
   将 `dist` 目录中的文件部署到Web服务器（如Nginx）

### Nginx配置示例

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 前端静态文件
    location / {
        root /path/to/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # 后端API代理
    location /api {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

### 使用Docker部署

1. **后端Dockerfile**
   ```dockerfile
   FROM python:3.9-slim
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt
   COPY . .
   CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "wsgi:application"]
   ```

2. **前端Dockerfile**
   ```dockerfile
   FROM node:14 AS builder
   WORKDIR /app
   COPY package*.json ./
   RUN npm install
   COPY . .
   RUN npm run build

   FROM nginx:alpine
   COPY --from=builder /app/dist /usr/share/nginx/html
   COPY nginx.conf /etc/nginx/conf.d/default.conf
   ```

3. **docker-compose.yml**
   ```yaml
   version: '3'
   services:
     backend:
       build: ./backend
       ports:
         - "5000:5000"
       environment:
         - FLASK_ENV=production
         - SECRET_KEY=${SECRET_KEY}
         - JWT_SECRET_KEY=${JWT_SECRET_KEY}
       volumes:
         - ./backend/logs:/app/logs

     frontend:
       build: ./frontend
       ports:
         - "80:80"
       depends_on:
         - backend
   ```

## 系统使用说明

### 登录系统

1. 访问系统首页，自动跳转到登录页
2. 输入用户名和密码登录
3. 新用户可点击"注册新账号"进行注册

### 台账管理

1. **查看台账列表**
   - 登录后自动进入台账列表页
   - 可通过搜索框、省份筛选、日期范围筛选数据
   - 点击表头可排序

2. **新增台账**
   - 点击"新增台账"按钮
   - 填写必填项（标*号的字段）
   - 项目名称支持输入联想
   - 点击"提交"保存

3. **编辑台账**
   - 在列表中点击"编辑"按钮
   - 修改需要的字段
   - 点击"保存修改"

4. **删除台账**
   - 在列表中点击"删除"按钮
   - 确认删除操作

5. **导出数据**
   - 点击"导出数据"按钮
   - 自动下载CSV格式文件

### 系统管理（仅管理员）

1. **查看系统日志**
   - 点击用户下拉菜单中的"系统管理"
   - 可按级别、用户、时间范围筛选日志

2. **查看系统统计**
   - 在系统日志页点击"系统统计"
   - 查看用户统计和台账统计信息

### 修改密码

1. 点击用户下拉菜单中的"修改密码"
2. 输入原密码和新密码
3. 确认后重新登录

## 常见问题

### 1. 后端启动失败
- 检查Python版本是否符合要求
- 确保虚拟环境已激活
- 检查依赖是否完全安装
- 查看logs目录下的日志文件

### 2. 前端无法连接后端
- 检查后端是否正在运行
- 确认代理配置是否正确（vue.config.js）
- 检查浏览器控制台的网络请求

### 3. 登录失败
- 确认用户名密码是否正确
- 检查后端日志中的错误信息
- 确保JWT密钥已正确配置

### 4. 权限问题
- 确认用户角色是否正确
- 管理员可以在数据库中修改用户角色
- 普通用户只能操作自己的数据

## 技术支持

如遇到问题，请检查：
1. 后端日志：`backend/logs/app.log`
2. 浏览器控制台错误信息
3. 网络请求状态（F12开发者工具）

## 安全建议

1. **生产环境必须修改**
   - SECRET_KEY
   - JWT_SECRET_KEY
   - 默认管理员密码

2. **定期备份数据库**
   - SQLite数据库文件：`backend/ledger.db`

3. **使用HTTPS**
   - 生产环境建议配置SSL证书

4. **限制CORS来源**
   - 修改`CORS_ORIGINS`为具体域名

5. **定期更新依赖**
   - 检查安全更新并及时升级

# 台账管理系统 - 项目总结和优化说明

## 项目优化要点

### 1. 后端优化

#### 代码结构优化
- **模块化设计**：将原始单文件拆分为多个模块（models、auth、api等）
- **配置管理**：使用环境变量和配置类管理不同环境的配置
- **蓝图架构**：使用Flask蓝图组织API路由，便于扩展和维护

#### 安全性增强
- **密钥管理**：敏感信息通过环境变量配置，不硬编码在代码中
- **错误处理**：统一的错误处理机制，避免敏感信息泄露
- **CORS配置**：支持跨域请求配置，生产环境可限制特定域名

#### 性能优化
- **数据库索引**：在常用查询字段（username、province、created_at）添加索引
- **分页查询**：列表接口支持分页，避免一次加载过多数据
- **查询优化**：使用SQLAlchemy的lazy loading减少不必要的数据加载

#### 功能增强
- **数据验证**：添加请求数据验证，确保数据完整性
- **日志记录**：完善的日志系统，记录操作日志和错误信息
- **数据导出**：支持CSV格式数据导出功能

### 2. 前端优化

#### 架构优化
- **组件化开发**：每个功能模块独立组件，提高复用性
- **状态管理**：使用Pinia集中管理用户状态
- **路由懒加载**：按需加载页面组件，提高初始加载速度

#### 用户体验
- **响应式设计**：适配不同屏幕尺寸
- **加载状态**：所有异步操作都有loading提示
- **错误提示**：友好的错误提示信息
- **表单验证**：前端表单验证，减少无效请求

#### 性能优化
- **请求拦截**：统一处理认证和错误
- **防抖处理**：搜索输入使用防抖减少请求次数
- **长文本处理**：使用Tooltip展示长文本，保持界面整洁

## 完整文件清单

### 后端文件（22个）

```
backend/
├── app/
│   ├── __init__.py              # 应用初始化和配置
│   ├── models.py                # 数据库模型定义
│   ├── auth.py                  # 用户认证模块
│   ├── config.py                # 配置文件
│   ├── api/
│   │   ├── __init__.py          # API包初始化
│   │   ├── ledger.py            # 台账相关API
│   │   ├── admin.py             # 管理员API
│   │   └── meta.py              # 元数据API（省份、建议等）
│   └── utils/
│       ├── __init__.py          # 工具包初始化
│       └── decorators.py        # 装饰器（角色权限检查）
├── scripts/                     # 脚本目录
│   ├── backup.bat               # Windows备份脚本
│   ├── backup.sh                # Linux备份脚本
│   ├── restore.bat              # Windows恢复脚本
│   ├── restore.sh               # Linux恢复脚本
│   ├── health_check.py          # 健康检查脚本
│   ├── performance_monitor.py   # 性能监控脚本
│   └── alert_config.py          # 告警配置
├── requirements.txt             # Python依赖列表
├── run.py                       # 开发环境启动脚本
├── wsgi.py                      # 生产环境WSGI入口
└── .env.example                 # 环境变量示例文件
```

### 前端文件（25个）

```
frontend/
├── public/
│   ├── index.html               # HTML入口文件
│   └── favicon.ico              # 网站图标
├── src/
│   ├── api/                     # API接口封装
│   │   ├── auth.js              # 认证相关API
│   │   ├── ledger.js            # 台账相关API
│   │   └── admin.js             # 管理员相关API
│   ├── router/
│   │   └── index.js             # 路由配置
│   ├── store/
│   │   └── user.js              # 用户状态管理
│   ├── utils/
│   │   └── request.js           # Axios请求封装
│   ├── views/                   # 页面组件
│   │   ├── LoginPage.vue        # 登录页面
│   │   ├── LedgerList.vue       # 台账列表页面
│   │   ├── LedgerForm.vue       # 台账表单页面
│   │   ├── AdminLogView.vue     # 管理员日志页面
│   │   └── NotFound.vue         # 404页面
│   ├── App.vue                  # 根组件
│   └── main.js                  # 应用入口
├── .env.development             # 开发环境配置
├── .env.production              # 生产环境配置
├── package.json                 # 项目依赖配置
├── package-lock.json            # 依赖版本锁定
└── vue.config.js                # Vue CLI配置
```

### 部署和文档文件（7个）

```
项目根目录/
├── README.md                    # 项目说明文档
├── deployment-guide.md          # 部署指南
├── install.bat                  # Windows安装脚本
├── install.sh                   # Linux安装脚本
├── start.bat                    # Windows启动脚本
├── start.sh                     # Linux启动脚本
└── docker-compose.yml           # Docker编排文件
```

**总计文件数：54个**

## 部署注意事项

### 1. 安全配置

- **必须修改的配置**：
  - `SECRET_KEY`：Flask会话密钥
  - `JWT_SECRET_KEY`：JWT签名密钥
  - `ADMIN_PASSWORD`：默认管理员密码

- **生产环境建议**：
  - 使用HTTPS协议
  - 配置防火墙规则
  - 定期更新依赖包
  - 启用日志审计

### 2. 性能优化

- **数据库优化**：
  - 大数据量时迁移到MySQL/PostgreSQL
  - 定期清理过期日志
  - 优化查询索引

- **缓存策略**：
  - 静态资源使用CDN
  - API响应缓存
  - 会话缓存

### 3. 监控运维

- **监控指标**：
  - API响应时间
  - 系统资源使用率
  - 错误日志统计
  - 用户活跃度

- **备份策略**：
  - 每日自动备份数据库
  - 保留7天本地备份
  - 重要数据上传云存储

### 4. 扩展建议

- **功能扩展**：
  - 添加数据统计图表
  - 支持文件附件上传
  - 增加审批流程
  - 集成消息通知

- **技术升级**：
  - 使用Redis缓存
  - 添加任务队列（Celery）
  - 微服务架构改造
  - 容器化部署

## 测试建议

### 单元测试

创建 `backend/tests/test_auth.py`：

```python
import pytest
from app import create_app, db
from app.models import User

@pytest.fixture
def client():
    app = create_app('testing')
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()

def test_user_registration(client):
    response = client.post('/api/register', json={
        'username': 'testuser',
        'password': 'testpass123'
    })
    assert response.status_code == 201
    assert response.json['success'] is True
```

### 性能测试

使用Apache Bench进行压力测试：

```bash
# 测试登录接口
ab -n 1000 -c 10 -p login.json -T application/json http://localhost:5000/api/login

# 测试列表接口
ab -n 1000 -c 10 -H "Authorization: Bearer YOUR_TOKEN" http://localhost:5000/api/ledger
```

## 总结

本项目通过以下优化实现了一个功能完善、结构清晰、易于维护的台账管理系统：

1. **代码质量**：模块化设计、统一错误处理、完善的日志系统
2. **安全性**：JWT认证、角色权限控制、环境变量配置
3. **用户体验**：响应式设计、友好的交互提示、高效的数据展示
4. **可维护性**：清晰的项目结构、详细的文档说明、自动化脚本
5. **可扩展性**：蓝图架构、组件化开发、标准化API设计

系统已具备生产环境部署的基本条件，可根据实际需求进行功能扩展和性能优化。