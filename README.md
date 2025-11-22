# 电商评论情感分析系统

一个基于爬虫与大模型情感分析的电商商品评论分析系统，支持京东、淘宝等平台的评论采集、清洗、情感分析和可视化展示。

## 系统架构

### 技术栈
- **前端**: React + TypeScript + Ant Design + ECharts
- **后端**: Node.js + NestJS + TypeScript
- **爬虫与分析**: Python + requests/Playwright + 大模型API
- **数据库**: MongoDB (推荐) / MySQL
- **任务调度**: Node.js 定时任务/队列

### 核心功能模块

1. **前端界面**
   - 新建分析任务
   - 商品评论可视化
   - 情感分析结果展示
   - 数据导出功能

2. **后端服务**
   - 任务管理API
   - 数据查询API
   - 任务调度
   - 数据库操作

3. **Python服务**
   - 电商平台爬虫
   - 评论数据清洗
   - 大模型情感分析
   - 数据预处理

## 项目结构

```
AI_comment_for_shop/
├── frontend/                 # React前端应用
├── backend/                  # NestJS后端服务
├── python-service/           # Python爬虫和分析服务
├── docs/                     # 文档
└── README.md
```

## 🚀 快速开始

### 环境要求
- **Node.js**: 16.x 或更高版本
- **Python**: 3.8 或更高版本  
- **MongoDB**: 4.4 或更高版本
- **操作系统**: Windows, macOS, Linux

### 一键启动（推荐）

```bash
# 1. 复制环境配置
cp .env.example .env

# 2. 配置OpenAI API密钥（必需）
# 编辑 .env 文件，设置 OPENAI_API_KEY=your_key_here

# 3. 启动所有服务
./start.sh start
```

### 手动启动

```bash
# 1. 安装依赖
./start.sh install

# 2. 启动后端服务
cd backend && npm run start:dev

# 3. 启动Python服务  
cd python-service && python main.py

# 4. 启动前端服务
cd frontend && npm run dev
```

### 访问系统

- **前端界面**: http://localhost:3000
- **后端API**: http://localhost:3001
- **Python服务**: http://localhost:8000

## 业务流程

1. 用户在前端创建分析任务
2. 后端记录任务并调度Python爬虫
3. Python爬虫采集评论数据
4. 数据清洗和预处理
5. 大模型情感分析
6. 结果聚合和可视化展示
7. 支持数据导出和任务管理

## 配置说明

系统支持配置多个电商平台、大模型API密钥、数据库连接等，具体配置请参考各模块的配置文件。
