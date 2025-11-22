# 电商评论情感分析系统 - 部署指南

## 系统架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   前端应用      │    │   后端API       │    │   Python服务    │
│   React + TS    │◄──►│   NestJS + TS   │◄──►│   FastAPI       │
│   Port: 3000    │    │   Port: 3001    │    │   Port: 8000    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                        ┌─────────────────┐
                        │   数据库         │
                        │   MongoDB       │
                        │   Port: 27017   │
                        └─────────────────┘
```

## 快速开始

### 1. 环境要求

- **Node.js**: 16.x 或更高版本
- **Python**: 3.8 或更高版本  
- **MongoDB**: 4.4 或更高版本
- **操作系统**: Windows, macOS, Linux

### 2. 安装步骤

#### 方法一：使用启动脚本（推荐）

```bash
# 1. 克隆项目
git clone <repository-url>
cd AI_comment_for_shop

# 2. 复制环境配置
cp .env.example .env

# 3. 编辑环境配置
# 修改 .env 文件，特别是 OPENAI_API_KEY

# 4. 启动系统
./start.sh start
```

#### 方法二：手动安装

```bash
# 1. 安装前端依赖
cd frontend
npm install

# 2. 安装后端依赖  
cd ../backend
npm install

# 3. 安装Python依赖
cd ../python-service
python3 -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate  # Windows
pip install -r requirements.txt

# 4. 启动MongoDB
mongod --dbpath ./data/db

# 5. 启动后端服务 (新终端)
cd backend
npm run start:dev

# 6. 启动Python服务 (新终端)  
cd python-service
source .venv/bin/activate
python main.py

# 7. 启动前端服务 (新终端)
cd frontend
npm run dev
```

### 3. 访问系统

- **前端界面**: http://localhost:3000
- **后端API**: http://localhost:3001
- **Python服务**: http://localhost:8000

## 环境配置

### 必需配置

1. **OpenAI API密钥**
   - 访问 https://platform.openai.com/ 获取API密钥
   - 在 `.env` 文件中设置 `OPENAI_API_KEY=your_key_here`

2. **MongoDB连接**
   - 本地安装MongoDB或使用云服务
   - 在 `.env` 文件中配置连接字符串

### 可选配置

- **其他大模型**: 可配置 Anthropic、Cohere 等替代方案
- **代理设置**: 如需代理访问，配置相关环境变量
- **日志级别**: 根据需求调整日志详细程度

## 生产环境部署

### Docker部署

```dockerfile
# 创建 docker-compose.yml
version: '3.8'
services:
  mongodb:
    image: mongo:6.0
    ports:
      - "27017:27017"
    volumes:
      - mongodb_data:/data/db

  backend:
    build: ./backend
    ports:
      - "3001:3001"
    environment:
      - MONGODB_URI=mongodb://mongodb:27017/
      - NODE_ENV=production
    depends_on:
      - mongodb

  python-service:
    build: ./python-service
    ports:
      - "8000:8000"
    environment:
      - MONGODB_URI=mongodb://mongodb:27017/
    depends_on:
      - mongodb

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend

volumes:
  mongodb_data:
```

### 云服务部署

#### MongoDB Atlas (推荐)
1. 注册 MongoDB Atlas 账户
2. 创建集群和数据库用户
3. 获取连接字符串
4. 更新 `.env` 中的 `MONGODB_URI`

#### Vercel (前端部署)
```bash
# 在前端目录
npm run build
vercel --prod
```

#### Railway/Render (后端部署)
- 连接GitHub仓库
- 配置环境变量
- 自动部署

## 系统监控

### 健康检查端点

- 前端: `http://localhost:3000`
- 后端: `http://localhost:3001/api/health`
- Python服务: `http://localhost:8000/`

### 日志查看

```bash
# 查看服务日志
tail -f data/mongodb.log
./start.sh status
```

## 故障排除

### 常见问题

1. **端口占用**
   ```bash
   # 查看端口占用
   lsof -i :3000
   lsof -i :3001  
   lsof -i :8000
   
   # 杀死占用进程
   kill -9 <PID>
   ```

2. **依赖安装失败**
   ```bash
   # 清理缓存重新安装
   rm -rf node_modules package-lock.json
   npm install
   ```

3. **MongoDB连接失败**
   - 检查MongoDB服务是否运行
   - 验证连接字符串格式
   - 检查防火墙设置

4. **OpenAI API错误**
   - 验证API密钥是否正确
   - 检查账户余额和配额
   - 确认网络连接

### 调试模式

```bash
# 启用详细日志
export LOG_LEVEL=DEBUG
./start.sh restart
```

## 备份与恢复

### 数据备份

```bash
# 备份MongoDB数据
mongodump --uri="mongodb://localhost:27017/ecommerce_analysis" --out=./backup/$(date +%Y%m%d)

# 恢复数据
mongorestore --uri="mongodb://localhost:27017/ecommerce_analysis" ./backup/20240101/
```

## 安全建议

1. **环境变量**: 不要将敏感信息提交到代码仓库
2. **API密钥**: 定期轮换API密钥
3. **防火墙**: 限制不必要的端口访问
4. **更新**: 定期更新依赖包和安全补丁

## 性能优化

### 数据库优化
- 为常用查询字段创建索引
- 定期清理过期数据
- 使用连接池

### 爬虫优化  
- 调整请求延迟避免被封
- 使用代理IP池
- 实现断点续爬

### 情感分析优化
- 批量处理减少API调用
- 实现结果缓存
- 使用更高效的模型

## 扩展开发

### 添加新的电商平台

1. 在 `python-service/crawler/` 创建新的爬虫类
2. 继承 `BaseCrawler` 基类
3. 实现 `crawl_comments` 方法
4. 在 `main.py` 中注册新爬虫

### 添加新的情感分析模型

1. 在 `sentiment_analyzer.py` 中添加新的API调用方法
2. 更新配置支持多模型切换
3. 实现模型结果标准化

## 技术支持

如遇问题，请：
1. 查看日志文件获取详细错误信息
2. 检查环境配置是否正确
3. 参考本文档的故障排除部分
4. 在项目Issues中提交问题
