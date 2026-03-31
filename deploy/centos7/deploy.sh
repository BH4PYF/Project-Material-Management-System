#!/bin/bash
# 材料管理系统 CentOS 7 自动部署脚本

set -e  # 遇到错误时退出

# 配置变量
PROJECT_NAME="material_system"
PROJECT_DIR="/home/django/${PROJECT_NAME}"
USER_NAME="django"
DOMAIN_NAME="your-domain.com"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

# 检查是否以root权限运行
if [[ $EUID -eq 0 ]]; then
   error "请不要以root用户运行此脚本"
fi

# 更新系统
log "更新系统..."
sudo yum update -y

# 安装依赖
log "安装系统依赖..."
sudo yum install -y epel-release
sudo yum install -y python3 python3-pip python3-devel gcc gcc-c++ make
sudo yum install -y sqlite-devel nginx
sudo yum install -y firewalld

# 创建部署用户
log "创建部署用户..."
if ! id "$USER_NAME" &>/dev/null; then
    sudo useradd -m -s /bin/bash "$USER_NAME"
    echo "$USER_NAME ALL=(ALL) NOPASSWD: ALL" | sudo tee /etc/sudoers.d/$USER_NAME
    warn "请为用户 $USER_NAME 设置密码"
else
    log "用户 $USER_NAME 已存在"
fi

# 切换到部署用户
log "切换到部署用户环境..."
sudo su - "$USER_NAME" << 'EOF'
set -e

# 创建项目目录
mkdir -p ~/material_system
cd ~/material_system

# 安装Python依赖
log "安装Python依赖..."
pip3 install --user -r requirements.txt

# 安装额外依赖
pip3 install --user gunicorn pysqlite3

# 配置Django设置
export DJANGO_SETTINGS_MODULE=material_system.settings
export DEBUG=False

# 数据库迁移
log "应用数据库迁移..."
python3 manage.py migrate

# 创建缓存表（DatabaseCache 需要）
log "创建缓存表..."
python3 manage.py createcachetable

# 创建管理员用户
log "创建管理员用户..."
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@example.com', 'Liyifeiniuniu1027-')" | python3 manage.py shell

# 收集静态文件
log "收集静态文件..."
python3 manage.py collectstatic --noinput

# 创建媒体目录
mkdir -p ~/material_system/media

EOF

# 配置systemd服务
log "配置systemd服务..."
sudo cp deploy/centos7/material-system.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable material-system

# 配置Nginx
log "配置Nginx..."
sudo cp deploy/centos7/nginx.conf /etc/nginx/conf.d/material-system.conf
# 替换域名
sudo sed -i "s/your-domain.com/${DOMAIN_NAME}/g" /etc/nginx/conf.d/material-system.conf

# 配置防火墙
log "配置防火墙..."
sudo systemctl enable firewalld
sudo systemctl start firewalld
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --reload

# 启动服务
log "启动服务..."
sudo systemctl start material-system
sudo systemctl start nginx

# 验证服务状态
log "验证服务状态..."
if sudo systemctl is-active --quiet material-system; then
    log "Django服务启动成功"
else
    error "Django服务启动失败"
fi

if sudo systemctl is-active --quiet nginx; then
    log "Nginx服务启动成功"
else
    error "Nginx服务启动失败"
fi

# 显示部署信息
echo
echo "=========================================="
echo "        部署完成！"
echo "=========================================="
echo "访问地址: http://${DOMAIN_NAME}"
echo "管理后台: http://${DOMAIN_NAME}/admin/"
echo "管理员账号: admin"
echo "管理员密码: Liyifeiniuniu1027-"
echo
echo "服务管理命令:"
echo "  sudo systemctl start material-system"
echo "  sudo systemctl stop material-system"
echo "  sudo systemctl restart material-system"
echo "  sudo systemctl status material-system"
echo
echo "日志查看:"
echo "  sudo journalctl -u material-system -f"
echo "  sudo tail -f /var/log/nginx/access.log"
echo "=========================================="