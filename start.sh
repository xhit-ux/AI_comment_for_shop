#!/bin/bash

# 电商评论情感分析系统启动脚本

echo "🚀 启动电商评论情感分析系统..."

# 检查必要的环境
check_environment() {
    echo "🔍 检查系统环境..."
    
    # 检查Node.js
    if ! command -v node &> /dev/null; then
        echo "❌ Node.js 未安装，请先安装 Node.js"
        exit 1
    fi
    
    # 检查Python
    if ! command -v python3 &> /dev/null; then
        echo "❌ Python3 未安装，请先安装 Python3"
        exit 1
    fi
    
    # 检查MongoDB
    if ! command -v mongod &> /dev/null; then
        echo "⚠️  MongoDB 未安装，请确保MongoDB服务正在运行"
    fi
    
    echo "✅ 环境检查完成"
}

# 安装依赖
install_dependencies() {
    echo "📦 安装依赖..."
    
    # 安装前端依赖
    echo "安装前端依赖..."
    cd frontend
    if [ ! -d "node_modules" ]; then
        npm install
    fi
    cd ..
    
    # 安装后端依赖
    echo "安装后端依赖..."
    cd backend
    if [ ! -d "node_modules" ]; then
        npm install
    fi
    cd ..
    
    # 安装Python依赖
    echo "安装Python依赖..."
    cd python-service
    if [ ! -f ".venv" ]; then
        python3 -m venv .venv
    fi
    source .venv/bin/activate
    pip install -r requirements.txt
    cd ..
    
    echo "✅ 依赖安装完成"
}

# 启动服务
start_services() {
    echo "🔄 启动服务..."
    
    # 启动MongoDB (如果本地运行)
    if command -v mongod &> /dev/null; then
        echo "启动MongoDB..."
        mongod --dbpath ./data/db --fork --logpath ./data/mongodb.log
    fi
    
    # 启动后端服务
    echo "启动后端服务..."
    cd backend
    npm run start:dev &
    BACKEND_PID=$!
    cd ..
    
    # 启动Python服务
    echo "启动Python服务..."
    cd python-service
    source .venv/bin/activate
    python main.py &
    PYTHON_PID=$!
    cd ..
    
    # 等待服务启动
    sleep 5
    
    # 启动前端服务
    echo "启动前端服务..."
    cd frontend
    npm run dev &
    FRONTEND_PID=$!
    cd ..
    
    # 保存进程ID
    echo $BACKEND_PID > .backend.pid
    echo $PYTHON_PID > .python.pid
    echo $FRONTEND_PID > .frontend.pid
    
    echo "✅ 所有服务已启动"
    echo ""
    echo "📊 服务访问地址:"
    echo "   前端: http://localhost:3000"
    echo "   后端API: http://localhost:3001"
    echo "   Python服务: http://localhost:8000"
    echo ""
    echo "🛑 停止服务请运行: ./stop.sh"
}

# 停止服务
stop_services() {
    echo "🛑 停止服务..."
    
    if [ -f ".backend.pid" ]; then
        kill $(cat .backend.pid) 2>/dev/null
        rm .backend.pid
    fi
    
    if [ -f ".python.pid" ]; then
        kill $(cat .python.pid) 2>/dev/null
        rm .python.pid
    fi
    
    if [ -f ".frontend.pid" ]; then
        kill $(cat .frontend.pid) 2>/dev/null
        rm .frontend.pid
    fi
    
    # 停止MongoDB
    if command -v mongod &> /dev/null; then
        pkill mongod
    fi
    
    echo "✅ 所有服务已停止"
}

# 显示服务状态
show_status() {
    echo "📊 服务状态:"
    
    if [ -f ".backend.pid" ] && kill -0 $(cat .backend.pid) 2>/dev/null; then
        echo "   后端服务: ✅ 运行中 (PID: $(cat .backend.pid))"
    else
        echo "   后端服务: ❌ 未运行"
    fi
    
    if [ -f ".python.pid" ] && kill -0 $(cat .python.pid) 2>/dev/null; then
        echo "   Python服务: ✅ 运行中 (PID: $(cat .python.pid))"
    else
        echo "   Python服务: ❌ 未运行"
    fi
    
    if [ -f ".frontend.pid" ] && kill -0 $(cat .frontend.pid) 2>/dev/null; then
        echo "   前端服务: ✅ 运行中 (PID: $(cat .frontend.pid))"
    else
        echo "   前端服务: ❌ 未运行"
    fi
}

# 主函数
main() {
    case "$1" in
        "start")
            check_environment
            install_dependencies
            start_services
            ;;
        "stop")
            stop_services
            ;;
        "restart")
            stop_services
            sleep 2
            start_services
            ;;
        "status")
            show_status
            ;;
        "install")
            check_environment
            install_dependencies
            ;;
        *)
            echo "使用方法: $0 {start|stop|restart|status|install}"
            echo ""
            echo "命令说明:"
            echo "  start    - 启动所有服务"
            echo "  stop     - 停止所有服务"
            echo "  restart  - 重启所有服务"
            echo "  status   - 显示服务状态"
            echo "  install  - 安装依赖"
            exit 1
            ;;
    esac
}

main "$@"
