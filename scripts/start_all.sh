#!/bin/bash
#
# 统一启动脚本 - 同时启动飞书机器人和 Web 管理界面
#
# 使用方法:
#   ./scripts/start_all.sh [development|production]
#
# 环境变量:
#   MODE - 运行模式 (development 或 production)
#   默认: development

set -e

# 确定运行模式
MODE="${1:-${MODE:-development}}"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 获取脚本目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_ROOT"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  飞书 AI 机器人 - 统一启动脚本${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 检查 .env 文件
if [ ! -f .env ]; then
    echo -e "${RED}错误: .env 文件不存在${NC}"
    echo "请从 .env.example 创建 .env 文件"
    exit 1
fi

# 加载环境变量
set -a
source .env
set +a

# 检查必需的环境变量
if [ -z "$FEISHU_APP_ID" ] || [ -z "$FEISHU_APP_SECRET" ]; then
    echo -e "${RED}错误: 缺少必需的飞书配置${NC}"
    echo "请在 .env 文件中设置 FEISHU_APP_ID 和 FEISHU_APP_SECRET"
    exit 1
fi

# 创建必要的目录
mkdir -p data logs

# PID 文件路径
BOT_PID_FILE="$PROJECT_ROOT/data/bot.pid"
WEB_PID_FILE="$PROJECT_ROOT/data/web.pid"

# 清理函数
cleanup() {
    echo ""
    echo -e "${YELLOW}正在停止服务...${NC}"
    
    # 停止机器人
    if [ -f "$BOT_PID_FILE" ]; then
        BOT_PID=$(cat "$BOT_PID_FILE")
        if ps -p $BOT_PID > /dev/null 2>&1; then
            echo -e "${YELLOW}停止飞书机器人 (PID: $BOT_PID)...${NC}"
            kill $BOT_PID
            wait $BOT_PID 2>/dev/null || true
        fi
        rm -f "$BOT_PID_FILE"
    fi
    
    # 停止 Web 服务
    if [ -f "$WEB_PID_FILE" ]; then
        WEB_PID=$(cat "$WEB_PID_FILE")
        if ps -p $WEB_PID > /dev/null 2>&1; then
            echo -e "${YELLOW}停止 Web 管理界面 (PID: $WEB_PID)...${NC}"
            kill $WEB_PID
            wait $WEB_PID 2>/dev/null || true
        fi
        rm -f "$WEB_PID_FILE"
    fi
    
    echo -e "${GREEN}所有服务已停止${NC}"
    exit 0
}

# 捕获退出信号
trap cleanup SIGINT SIGTERM

echo -e "${GREEN}运行模式: ${MODE}${NC}"
echo ""

# 启动飞书机器人
echo -e "${BLUE}[1/2] 启动飞书机器人...${NC}"
python lark_bot.py > logs/bot.log 2>&1 &
BOT_PID=$!
echo $BOT_PID > "$BOT_PID_FILE"
echo -e "${GREEN}✓ 飞书机器人已启动 (PID: $BOT_PID)${NC}"
echo -e "  日志文件: logs/bot.log"
echo ""

# 等待机器人启动
sleep 2

# 检查机器人是否正常运行
if ! ps -p $BOT_PID > /dev/null 2>&1; then
    echo -e "${RED}✗ 飞书机器人启动失败${NC}"
    echo "请查看日志: logs/bot.log"
    cleanup
fi

# 启动 Web 管理界面
echo -e "${BLUE}[2/2] 启动 Web 管理界面...${NC}"

case "$MODE" in
    development|dev)
        echo -e "${GREEN}使用开发模式 (Flask dev server)${NC}"
        python -m feishu_bot.web_admin.server \
            --host "${WEB_ADMIN_HOST:-0.0.0.0}" \
            --port "${WEB_ADMIN_PORT:-8080}" \
            --debug \
            --log-level DEBUG > logs/web.log 2>&1 &
        WEB_PID=$!
        ;;
    
    production|prod)
        echo -e "${GREEN}使用生产模式 (Gunicorn)${NC}"
        
        # 检查 gunicorn 是否安装
        if ! command -v gunicorn &> /dev/null; then
            echo -e "${RED}错误: Gunicorn 未安装${NC}"
            echo "安装命令: pip install gunicorn"
            cleanup
        fi
        
        gunicorn -c gunicorn.conf.py wsgi:app > logs/web.log 2>&1 &
        WEB_PID=$!
        ;;
    
    *)
        echo -e "${RED}错误: 无效的运行模式 '$MODE'${NC}"
        echo "使用方法: $0 [development|production]"
        cleanup
        ;;
esac

echo $WEB_PID > "$WEB_PID_FILE"
echo -e "${GREEN}✓ Web 管理界面已启动 (PID: $WEB_PID)${NC}"
echo -e "  访问地址: http://${WEB_ADMIN_HOST:-0.0.0.0}:${WEB_ADMIN_PORT:-8080}"
echo -e "  日志文件: logs/web.log"
echo ""

# 等待 Web 服务启动
sleep 2

# 检查 Web 服务是否正常运行
if ! ps -p $WEB_PID > /dev/null 2>&1; then
    echo -e "${RED}✗ Web 管理界面启动失败${NC}"
    echo "请查看日志: logs/web.log"
    cleanup
fi

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  所有服务启动成功！${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${BLUE}服务状态:${NC}"
echo -e "  • 飞书机器人: ${GREEN}运行中${NC} (PID: $BOT_PID)"
echo -e "  • Web 管理界面: ${GREEN}运行中${NC} (PID: $WEB_PID)"
echo ""
echo -e "${BLUE}日志查看:${NC}"
echo -e "  • 机器人日志: tail -f logs/bot.log"
echo -e "  • Web 日志: tail -f logs/web.log"
echo ""
echo -e "${YELLOW}按 Ctrl+C 停止所有服务${NC}"
echo ""

# 保持脚本运行，等待信号
wait
