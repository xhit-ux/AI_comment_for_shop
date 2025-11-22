#!/bin/bash

# 电商评论情感分析系统停止脚本

echo "🛑 停止电商评论情感分析系统..."

# 停止服务
stop_services() {
    echo "停止所有服务..."
    
    # 停止前端服务
    if [ -f ".frontend.pid" ]; then
        FRONTEND_PID=$(cat .frontend.pid)
        if kill -0 $FRONTEND_PID 2>/dev/null; then
            echo "停止前端服务 (PID: $FRONTEND_PID)..."
            kill $FRONTEND_PID
        fi
        rm .frontend.pid
    fi
    
    # 停止后端服务
    if [ -f ".backend.pid" ]; then
        BACKEND_PID=$(cat .backend.pid)
        if kill -0 $BACKEND_PID 2>/dev/null; then
            echo "停止后端服务 (PID: $BACKEND_PID)..."
            kill $BACKEND_PID
        fi
        rm .backend.pid
    fi
    
    # 停止Python服务
    if [ -f ".python.pid" ]; then
        PYTHON_PID=$(cat .python.pid)
        if kill -0 $PYTHON_PID 2>/dev/null; then
            echo "停止Python服务 (PID: $PYTHON_PID)..."
            kill $PYTHON_PID
        fi
        rm .python.pid
    fi
    
    # 停止MongoDB (如果由脚本启动)
    if [ -f ".mongodb.pid" ]; then
        MONGODB_PID=$(cat .mongodb.pid)
        if kill -0 $MONGODB_PID 2>/dev/null; then
            echo "停止MongoDB (PID: $MONGODB_PID)..."
            kill $MONGODB_PID
        fi
        rm .mongodb.pid
    fi
    
    # 清理可能残留的进程
    pkill -f "node.*frontend" 2>/dev/null
    pkill -f "node.*backend" 2>/dev/null
    pkill -f "python.*main.py" 2>/dev/null
    
    echo "✅ 所有服务已停止"
}

# 强制停止
force_stop() {
    echo "⚠️  强制停止所有服务..."
    
    # 强制杀死所有相关进程
    pkill -9 -f "npm run dev" 2>/dev/null
    pkill -9 -f "nest start" 2>/dev/null
    pkill -9 -f "python main.py" 2>/dev/null
    
    # 清理PID文件
    rm -f .frontend.pid .backend.pid .python.pid .mongodb.pid
    
    echo "✅ 强制停止完成"
}

# 显示服务状态
show_status() {
    echo "📊 当前服务状态:"
    
    if [ -f ".frontend.pid" ] && kill -0 $(cat .frontend.pid) 2>/dev/null; then
        echo "   前端服务: ✅ 运行中"
    else
        echo "   前端服务: ❌ 未运行"
    fi
    
    if [ -f ".backend.pid" ] && kill -0 $(cat .backend.pid) 2>/dev/null; then
        echo "   后端服务: ✅ 运行中"
    else
        echo "   后端服务: ❌ 未运行"
    fi
    
    if [ -f ".python.pid" ] && kill -0 $(cat .python.pid) 2>/dev/null; then
        echo "   Python服务: ✅ 运行中"
    else
        echo "   Python服务: ❌ 未运行"
    fi
}

# 主函数
main() {
    case "$1" in
        "status")
            show_status
            ;;
        "force")
            force_stop
            ;;
        *)
            stop_services
            ;;
    esac
}

main "$@"
