#!/bin/bash

# 飞书AI机器人部署脚本
# 用法: ./deploy.sh [start|stop|restart|logs|status|update]

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 函数：打印信息
info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

# 函数：打印警告
warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

# 函数：打印错误
error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查 Docker 是否安装
check_docker() {
    if ! command -v docker &> /dev/null; then
        error "Docker 未安装，请先安装 Docker"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        warn "Docker Compose 未安装，将使用 docker 命令"
        USE_COMPOSE=false
    else
        USE_COMPOSE=true
    fi
}

# 检查配置文件
check_config() {
    if [ ! -f .env ]; then
        error ".env 文件不存在"
        info "请复制 .env.example 并填入配置："
        echo "  cp .env.example .env"
        echo "  nano .env"
        exit 1
    fi
}

# 启动服务
start() {
    info "启动飞书AI机器人..."
    check_docker
    check_config
    
    if [ "$USE_COMPOSE" = true ]; then
        docker-compose up -d
        info "服务已启动（使用 Docker Compose）"
    else
        # 构建镜像
        docker build -t feishu-ai-bot .
        
        # 停止并删除旧容器（如果存在）
        docker stop feishu-ai-bot 2>/dev/null || true
        docker rm feishu-ai-bot 2>/dev/null || true
        
        # 启动新容器
        docker run -d \
            --name feishu-ai-bot \
            --restart unless-stopped \
            --env-file .env \
            -v "$(pwd)/data:/app/data" \
            feishu-ai-bot
        
        info "服务已启动（使用 Docker）"
    fi
    
    info "查看日志: ./deploy.sh logs"
}

# 停止服务
stop() {
    info "停止飞书AI机器人..."
    check_docker
    
    if [ "$USE_COMPOSE" = true ]; then
        docker-compose down
    else
        docker stop feishu-ai-bot
        docker rm feishu-ai-bot
    fi
    
    info "服务已停止"
}

# 重启服务
restart() {
    info "重启飞书AI机器人..."
    stop
    sleep 2
    start
}

# 查看日志
logs() {
    check_docker
    
    if [ "$USE_COMPOSE" = true ]; then
        docker-compose logs -f --tail=100
    else
        docker logs -f --tail=100 feishu-ai-bot
    fi
}

# 查看状态
status() {
    check_docker
    
    info "服务状态："
    
    if [ "$USE_COMPOSE" = true ]; then
        docker-compose ps
    else
        docker ps -a --filter name=feishu-ai-bot
    fi
    
    echo ""
    info "资源使用："
    docker stats --no-stream feishu-ai-bot 2>/dev/null || warn "容器未运行"
}

# 更新服务
update() {
    info "更新飞书AI机器人..."
    
    # 拉取最新代码
    if [ -d .git ]; then
        info "拉取最新代码..."
        git pull
    else
        warn "不是 Git 仓库，跳过代码更新"
    fi
    
    # 重新构建并启动
    check_docker
    check_config
    
    if [ "$USE_COMPOSE" = true ]; then
        docker-compose up -d --build
    else
        # 构建新镜像
        docker build -t feishu-ai-bot .
        
        # 停止旧容器
        docker stop feishu-ai-bot 2>/dev/null || true
        docker rm feishu-ai-bot 2>/dev/null || true
        
        # 启动新容器
        docker run -d \
            --name feishu-ai-bot \
            --restart unless-stopped \
            --env-file .env \
            -v "$(pwd)/data:/app/data" \
            feishu-ai-bot
    fi
    
    info "服务已更新"
}

# 备份数据
backup() {
    info "备份会话数据..."
    
    BACKUP_DIR="backups"
    BACKUP_FILE="backup-$(date +%Y%m%d-%H%M%S).tar.gz"
    
    mkdir -p "$BACKUP_DIR"
    
    if [ -d data ]; then
        tar -czf "$BACKUP_DIR/$BACKUP_FILE" data/
        info "备份完成: $BACKUP_DIR/$BACKUP_FILE"
    else
        warn "data 目录不存在，无需备份"
    fi
}

# 显示帮助
help() {
    echo "飞书AI机器人部署脚本"
    echo ""
    echo "用法: ./deploy.sh [命令]"
    echo ""
    echo "命令:"
    echo "  start    - 启动服务"
    echo "  stop     - 停止服务"
    echo "  restart  - 重启服务"
    echo "  logs     - 查看日志"
    echo "  status   - 查看状态"
    echo "  update   - 更新服务"
    echo "  backup   - 备份数据"
    echo "  help     - 显示帮助"
    echo ""
    echo "示例:"
    echo "  ./deploy.sh start    # 启动服务"
    echo "  ./deploy.sh logs     # 查看日志"
    echo "  ./deploy.sh update   # 更新服务"
}

# 主函数
main() {
    case "${1:-help}" in
        start)
            start
            ;;
        stop)
            stop
            ;;
        restart)
            restart
            ;;
        logs)
            logs
            ;;
        status)
            status
            ;;
        update)
            update
            ;;
        backup)
            backup
            ;;
        help|--help|-h)
            help
            ;;
        *)
            error "未知命令: $1"
            help
            exit 1
            ;;
    esac
}

# 运行主函数
main "$@"
