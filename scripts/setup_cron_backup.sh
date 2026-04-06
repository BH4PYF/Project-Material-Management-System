#!/bin/bash
# 一键设置数据库定时备份
# 用法：bash scripts/setup_cron_backup.sh

set -e

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
CRON_FILE="$PROJECT_DIR/scripts/backup_crontab.example"
LOG_FILE="$PROJECT_DIR/logs/backup.log"

echo "=================================="
echo "数据库定时备份设置向导"
echo "=================================="
echo ""

# 检查 crontab 命令
if ! command -v crontab &> /dev/null; then
    echo "❌ 错误：crontab 命令未找到，请先安装 cron 服务"
    exit 1
fi

echo "✅ 检测到项目目录：$PROJECT_DIR"
echo ""

# 创建日志目录
mkdir -p "$(dirname "$LOG_FILE")"
echo "✅ 创建日志目录：$(dirname "$LOG_FILE")"

# 显示当前 crontab 配置
echo ""
echo "📋 当前的 crontab 配置："
echo "--------------------------------"
crontab -l 2>/dev/null || echo "(无配置)"
echo ""

# 询问用户选择
echo "请选择备份策略："
echo "1. 每天凌晨 2 点备份（保留 30 天）- 推荐"
echo "2. 每天 + 每周双重备份"
echo "3. 手动查看示例配置"
echo "4. 取消"
echo ""
read -p "请输入选项 [1-4]: " choice

case $choice in
    1)
        # 每天备份
        CRON_JOB="0 2 * * * cd $PROJECT_DIR && bash scripts/backup_db.sh 30 >> $LOG_FILE 2>&1"
        echo ""
        echo "✅ 将添加以下定时任务："
        echo "   $CRON_JOB"
        read -p "确认添加？[y/N]: " confirm
        if [[ $confirm == [yY] ]]; then
            (crontab -l 2>/dev/null | grep -v "backup_db.sh"; echo "$CRON_JOB") | crontab -
            echo "✅ 定时备份已启用！"
        else
            echo "❌ 已取消"
            exit 0
        fi
        ;;
    2)
        # 双重备份
        echo ""
        echo "✅ 将添加两个定时任务："
        DAILY_JOB="0 2 * * * cd $PROJECT_DIR && bash scripts/backup_db.sh 30 >> $LOG_FILE 2>&1"
        WEEKLY_JOB="0 3 * * 0 cd $PROJECT_DIR && bash scripts/backup_db.sh 90 >> ${LOG_FILE/.log/_weekly.log} 2>&1"
        echo "   每日：$DAILY_JOB"
        echo "   每周：$WEEKLY_JOB"
        read -p "确认添加？[y/N]: " confirm
        if [[ $confirm == [yY] ]]; then
            (crontab -l 2>/dev/null | grep -v "backup_db.sh"; echo "$DAILY_JOB"; echo "$WEEKLY_JOB") | crontab -
            echo "✅ 双重定时备份已启用！"
        else
            echo "❌ 已取消"
            exit 0
        fi
        ;;
    3)
        echo ""
        echo "📄 示例配置文件内容："
        echo "--------------------------------"
        cat "$CRON_FILE"
        echo ""
        echo "💡 提示：使用以下命令应用此配置："
        echo "   crontab $CRON_FILE"
        exit 0
        ;;
    4)
        echo "❌ 已取消"
        exit 0
        ;;
    *)
        echo "❌ 无效的选项"
        exit 1
        ;;
esac

# 验证配置
echo ""
echo "📋 验证 crontab 配置："
echo "--------------------------------"
crontab -l | grep backup_db.sh

# 检查 cron 服务状态
echo ""
if systemctl is-active --quiet cron; then
    echo "✅ Cron 服务正在运行"
else
    echo "⚠️  Cron 服务未运行，尝试启动..."
    if command -v systemctl &> /dev/null; then
        sudo systemctl start cron 2>/dev/null && echo "✅ Cron 服务已启动" || echo "⚠️  无法启动 Cron 服务，请手动处理"
    fi
fi

echo ""
echo "=================================="
echo "设置完成！"
echo "=================================="
echo ""
echo "📊 使用说明："
echo "  • 手动备份：bash scripts/backup_db.sh"
echo "  • 查看日志：tail -f logs/backup.log"
echo "  • 查看备份：ls -lh backups/"
echo "  • 移除定时：crontab -e (删除对应行)"
echo ""
