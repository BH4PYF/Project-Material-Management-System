#!/bin/bash
# 材料管理系统监控脚本

# 配置变量
PROJECT_NAME="material_system"
SERVICE_NAME="material-system"
LOG_FILE="/var/log/${PROJECT_NAME}_monitor.log"
ALERT_EMAIL="admin@your-domain.com"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 日志函数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# 发送告警邮件
send_alert() {
    local subject="$1"
    local message="$2"
    
    log "发送告警: $subject"
    
    # 可以配置邮件发送，这里只是记录日志
    # echo "$message" | mail -s "$subject" "$ALERT_EMAIL"
}

# 检查服务状态
check_service_status() {
    if systemctl is-active --quiet "$SERVICE_NAME"; then
        log "✓ 服务 $SERVICE_NAME 运行正常"
        return 0
    else
        log "✗ 服务 $SERVICE_NAME 已停止"
        send_alert "服务告警: $SERVICE_NAME 停止运行" "服务 $SERVICE_NAME 在 $(hostname) 上已停止运行"
        return 1
    fi
}

# 检查端口监听
check_port_listening() {
    local port=8000
    if netstat -tlnp | grep -q ":$port "; then
        log "✓ 端口 $port 监听正常"
        return 0
    else
        log "✗ 端口 $port 未监听"
        send_alert "端口告警: $port 端口未监听" "端口 $port 在 $(hostname) 上未被监听"
        return 1
    fi
}

# 检查数据库文件
check_database() {
    local db_file="/home/django/material_system/db.sqlite3"
    if [ -f "$db_file" ] && [ -s "$db_file" ]; then
        log "✓ 数据库文件正常"
        return 0
    else
        log "✗ 数据库文件异常"
        send_alert "数据库告警: 数据库文件异常" "数据库文件 $db_file 在 $(hostname) 上异常"
        return 1
    fi
}

# 检查磁盘空间
check_disk_space() {
    local threshold=90  # 90% 阈值
    local usage=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
    
    if [ "$usage" -lt "$threshold" ]; then
        log "✓ 磁盘空间充足 (${usage}%)"
        return 0
    else
        log "✗ 磁盘空间不足 (${usage}%)"
        send_alert "磁盘告警: 磁盘空间不足" "磁盘使用率 ${usage}%，超过阈值 ${threshold}%"
        return 1
    fi
}

# 检查内存使用
check_memory_usage() {
    local threshold=85  # 85% 阈值
    local usage=$(free | grep Mem | awk '{printf("%.0f", $3/$2 * 100.0)}')
    
    if [ "$usage" -lt "$threshold" ]; then
        log "✓ 内存使用正常 (${usage}%)"
        return 0
    else
        log "✗ 内存使用过高 (${usage}%)"
        send_alert "内存告警: 内存使用过高" "内存使用率 ${usage}%，超过阈值 ${threshold}%"
        return 1
    fi
}

# 检查CPU使用率
check_cpu_usage() {
    local threshold=80  # 80% 阈值
    local usage=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | sed 's/%us,//')
    usage=$(echo "$usage" | cut -d'.' -f1)  # 取整数部分
    
    if [ "$usage" -lt "$threshold" ]; then
        log "✓ CPU使用正常 (${usage}%)"
        return 0
    else
        log "✗ CPU使用过高 (${usage}%)"
        send_alert "CPU告警: CPU使用过高" "CPU使用率 ${usage}%，超过阈值 ${threshold}%"
        return 1
    fi
}

# 检查HTTP响应
check_http_response() {
    local url="http://localhost:8000/health/"
    local timeout=10
    
    if curl -s --max-time $timeout "$url" > /dev/null; then
        log "✓ HTTP服务响应正常"
        return 0
    else
        log "✗ HTTP服务无响应"
        send_alert "HTTP告警: 服务无响应" "HTTP服务 $url 在 $(hostname) 上无响应"
        return 1
    fi
}

# 重启服务
restart_service() {
    log "尝试重启服务 $SERVICE_NAME"
    sudo systemctl restart "$SERVICE_NAME"
    
    # 等待服务启动
    sleep 10
    
    if systemctl is-active --quiet "$SERVICE_NAME"; then
        log "✓ 服务重启成功"
        send_alert "服务恢复: $SERVICE_NAME 重启成功" "服务 $SERVICE_NAME 在 $(hostname) 上重启成功"
    else
        log "✗ 服务重启失败"
        send_alert "服务告警: $SERVICE_NAME 重启失败" "服务 $SERVICE_NAME 在 $(hostname) 上重启失败"
    fi
}

# 主监控函数
main_monitor() {
    log "========================================"
    log "开始执行监控检查"
    log "========================================"
    
    local errors=0
    
    # 执行各项检查
    check_service_status || ((errors++))
    check_port_listening || ((errors++))
    check_database || ((errors++))
    check_disk_space || ((errors++))
    check_memory_usage || ((errors++))
    check_cpu_usage || ((errors++))
    check_http_response || ((errors++))
    
    log "========================================"
    log "监控检查完成，发现 $errors 个问题"
    log "========================================"
    
    # 如果有错误且启用了自动重启
    if [ "$errors" -gt 0 ] && [ "$AUTO_RESTART" = "true" ]; then
        restart_service
    fi
}

# 显示系统信息
show_system_info() {
    echo "=== 系统信息 ==="
    echo "主机名: $(hostname)"
    echo "系统时间: $(date)"
    echo "运行时间: $(uptime)"
    echo ""
    echo "=== 资源使用 ==="
    echo "内存使用: $(free -h | grep Mem | awk '{print $3"/"$2" ("$3/$2*100"%)" }')"
    echo "磁盘使用: $(df -h / | tail -1 | awk '{print $3"/"$2" ("$5")"}')"
    echo "CPU负载: $(uptime | awk -F'load average:' '{print $2}')"
    echo ""
    echo "=== 服务状态 ==="
    systemctl status "$SERVICE_NAME" --no-pager -l
}

# 显示帮助
show_help() {
    echo "材料管理系统监控工具"
    echo ""
    echo "用法:"
    echo "  $0 check          - 执行完整监控检查"
    echo "  $0 info           - 显示系统信息"
    echo "  $0 restart        - 重启服务"
    echo "  $0 status         - 检查服务状态"
    echo "  $0 help           - 显示此帮助"
    echo ""
    echo "环境变量:"
    echo "  AUTO_RESTART=true - 启用自动重启功能"
    echo ""
    echo "示例:"
    echo "  $0 check"
    echo "  AUTO_RESTART=true $0 check"
    echo "  $0 info"
}

# 主程序
case "$1" in
    check)
        main_monitor
        ;;
    info)
        show_system_info
        ;;
    restart)
        restart_service
        ;;
    status)
        systemctl status "$SERVICE_NAME" --no-pager
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        show_help
        exit 1
        ;;
esac