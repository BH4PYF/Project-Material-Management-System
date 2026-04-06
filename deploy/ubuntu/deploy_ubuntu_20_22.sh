#!/bin/bash
# Ubuntu 部署脚本 - 材料管理系统
# 用法: sudo bash deploy_ubuntu.sh

set -e  # 出错即停

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  材料管理系统 Ubuntu 部署脚本${NC}"
echo -e "${GREEN}========================================${NC}"

# 检查是否以 root 运行
if [ "$EUID" -ne 0 ]; then 
   echo -e "${RED}请以 root 权限运行此脚本: sudo bash deploy_ubuntu.sh${NC}" 
   exit 1
fi

# 获取当前用户名（非 root）
REAL_USER=${SUDO_USER:-$USER}
if [ "$REAL_USER" = "root" ]; then
    echo -e "${YELLOW}警告: 当前为 root 用户，建议使用普通用户部署${NC}"
    read -p "是否继续? (y/n) " -n 1 -r
    echo
    if [[ ! $REAL_USER =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi
HOME_DIR=$(eval echo ~$REAL_USER)

echo -e "\n${GREEN}[1/7] 更新系统并安装依赖...${NC}"
apt update
apt upgrade -y
apt install -y python3 python3-pip python3-venv git nginx redis-server

# 安装系统级 Python 包
apt install -y python3-dev default-libmysqlclient-dev build-essential pkg-config

echo -e "\n${GREEN}[2/7] 配置项目目录...${NC}"
APP_DIR="$HOME_DIR/material-system"
mkdir -p $APP_DIR

# 如果当前目录有代码，则复制；否则从 GitHub 克隆
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
if [ -f "$SCRIPT_DIR/manage.py" ]; then
    echo -e "${YELLOW}检测到本地项目，正在复制...${NC}"
    cp -r "$SCRIPT_DIR"/* $APP_DIR/
    cp -r "$SCRIPT_DIR"/.[^.]* $APP_DIR/ 2>/dev/null || true
else
    echo -e "${YELLOW}未找到本地项目，从 GitHub 克隆...${NC}"
    git clone https://github.com/BH4PYF/Project-Material-Management-System.git $APP_DIR
fi

chown -R $REAL_USER:$REAL_USER $APP_DIR
cd $APP_DIR

echo -e "\n${GREEN}[3/7] 创建虚拟环境并安装 Python 依赖...${NC}"
sudo -u $REAL_USER python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install gunicorn pymysql python-dotenv
if [ -f requirements.txt ]; then
    pip install -r requirements.txt
else
    # 如果没有 requirements.txt，安装基础依赖
    pip install django>=4.2 openpyxl
fi

# 生成或更新 requirements.txt
pip freeze > requirements.txt

echo -e "\n${GREEN}[4/7] 配置 Django 生产环境...${NC}"
# 生成随机密钥
SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(50))")

# 修改 settings.py 生产配置
cat > material_system/production_settings.py << EOF
"""生产环境配置"""
from .settings import *

DEBUG = False
ALLOWED_HOSTS = ['*']  # 生产环境请替换为实际域名或IP

# 使用更安全的密钥
SECRET_KEY = '$SECRET_KEY'

# 静态文件收集
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'

# 安全配置
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = False  # 如果使用 HTTPS 则设为 True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'

# 日志配置
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
        },
    },
    'root': {
        'handlers': ['file'],
        'level': 'INFO',
    },
}
EOF

mkdir -p logs
chown -R $REAL_USER:$REAL_USER logs

echo -e "\n${GREEN}[5/7] 初始化数据库...${NC}"
# 询问是否需要清除所有数据
echo -e "${YELLOW}是否清除所有现有数据并重新初始化？(y/n)${NC}"
read -n 1 -r RESET_DB
echo
if [[ $RESET_DB =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}正在清除所有数据...${NC}"
    sudo -u $REAL_USER bash -c "cd $APP_DIR && source venv/bin/activate && python manage.py flush --noinput --settings=material_system.production_settings"
    echo -e "${GREEN}数据已清除，正在重新迁移...${NC}"
fi

sudo -u $REAL_USER bash -c "cd $APP_DIR && source venv/bin/activate && python manage.py migrate --settings=material_system.production_settings"
sudo -u $REAL_USER bash -c "cd $APP_DIR && source venv/bin/activate && python manage.py createcachetable --settings=material_system.production_settings"
sudo -u $REAL_USER bash -c "cd $APP_DIR && source venv/bin/activate && python manage.py collectstatic --noinput --settings=material_system.production_settings"

# 创建默认管理员账号
echo -e "\n${GREEN}创建管理员账号...${NC}"
sudo -u $REAL_USER bash -c "cd $APP_DIR && source venv/bin/activate && python manage.py shell << 'PYTHON_EOF'
from django.contrib.auth import get_user_model
User = get_user_model()

# 删除已存在的 admin 用户
User.objects.filter(username='admin').delete()

# 创建 admin 用户
User.objects.create_superuser('admin', 'admin@example.com', 'admin')
print('✅ 管理员账号已创建：用户名=admin, 密码=admin')
PYTHON_EOF"
fi

echo -e "\n${GREEN}[6/7] 配置 Gunicorn 系统服务...${NC}"
cat > /etc/systemd/system/material-system.service << EOF
[Unit]
Description=Material System Gunicorn Service
After=network.target

[Service]
User=$REAL_USER
Group=$REAL_USER
WorkingDirectory=$APP_DIR
Environment="PATH=$APP_DIR/venv/bin"
ExecStart=$APP_DIR/venv/bin/gunicorn --workers 3 --bind unix:$APP_DIR/material-system.sock material_system.wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable material-system.service
systemctl start material-system.service

echo -e "\n${GREEN}[7/7] 配置 Nginx...${NC}"
# 获取服务器 IP
SERVER_IP=$(hostname -I | awk '{print $1}')

cat > /etc/nginx/sites-available/material-system << EOF
server {
    listen 80;
    server_name $SERVER_IP;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        alias $APP_DIR/staticfiles/;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:$APP_DIR/material-system.sock;
    }
}
EOF

ln -sf /etc/nginx/sites-available/material-system /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx

# 配置防火墙（如果启用）
if command -v ufw &> /dev/null; then
    ufw allow 80/tcp
    ufw allow 22/tcp
    echo -e "${YELLOW}防火墙已开放 80 端口${NC}"
fi

echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}✅ 部署完成！${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "访问地址: http://$SERVER_IP"
echo -e "项目路径: $APP_DIR"
echo -e "日志文件: journalctl -u material-system -f"
echo -e "\n${YELLOW}后续命令：${NC}"
echo -e "重启服务: sudo systemctl restart material-system"
echo -e "查看状态: sudo systemctl status material-system"
echo -e "修改配置后重载: sudo systemctl daemon-reload && sudo systemctl restart material-system"
echo -e "\n${GREEN}如有问题，检查日志：${NC}"
echo -e "journalctl -u material-system -n 50 --no-pager"
echo -e "tail -f $APP_DIR/logs/django.log"
