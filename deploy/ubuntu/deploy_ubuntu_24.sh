#!/bin/bash
# Ubuntu 24.04 部署脚本 - 材料管理系统
# 用法: sudo bash deploy_ubuntu_24.sh

set -e  # 出错即停

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  材料管理系统 Ubuntu 24.04 部署脚本${NC}"
echo -e "${GREEN}========================================${NC}"

# 检查是否以 root 运行
if [ "$EUID" -ne 0 ]; then 
   echo -e "${RED}请以 root 权限运行此脚本: sudo bash deploy_ubuntu_24.sh${NC}" 
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

# Ubuntu 24.04 默认 Python 3.12，安装开发包
apt install -y python3-dev build-essential pkg-config libssl-dev

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
    pip install django>=4.2 openpyxl
fi

# 生成或更新 requirements.txt
pip freeze > requirements.txt

echo -e "\n${GREEN}[4/7] 配置 Django 生产环境...${NC}"
# 生成随机密钥
SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(50))")

# 创建 .env 文件（如果不存在）
if [ ! -f .env ]; then
    sudo -u $REAL_USER cp .env.example .env
    sudo -u $REAL_USER sed -i "s/^SECRET_KEY=.*/SECRET_KEY=$SECRET_KEY/" .env
    sudo -u $REAL_USER sed -i 's/^DEBUG=.*/DEBUG=False/' .env
fi

# 创建日志目录
mkdir -p logs
chown -R $REAL_USER:$REAL_USER logs

echo -e "\n${GREEN}[5/7] 初始化数据库...${NC}"
# 询问是否需要清除所有数据
echo -e "${YELLOW}是否清除所有现有数据并重新初始化？(y/n)${NC}"
read -n 1 -r RESET_DB
echo
if [[ $RESET_DB =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}正在清除所有数据...${NC}"
    sudo -u $REAL_USER bash -c "cd $APP_DIR && source venv/bin/activate && python manage.py flush --noinput"
    echo -e "${GREEN}数据已清除，正在重新迁移...${NC}"
fi

sudo -u $REAL_USER bash -c "cd $APP_DIR && source venv/bin/activate && python manage.py migrate"
sudo -u $REAL_USER bash -c "cd $APP_DIR && source venv/bin/activate && python manage.py createcachetable"
sudo -u $REAL_USER bash -c "cd $APP_DIR && source venv/bin/activate && python manage.py collectstatic --noinput"

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

    client_max_body_size 20M;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        alias $APP_DIR/staticfiles/;
        expires 30d;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:$APP_DIR/material-system.sock;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

ln -sf /etc/nginx/sites-available/material-system /etc/nginx/sites-enabled/
# 移除默认站点
rm -f /etc/nginx/sites-enabled/default

nginx -t && systemctl reload nginx

# 配置防火墙（如果启用）
if command -v ufw &> /dev/null; then
    ufw allow 80/tcp
    ufw allow 22/tcp
    echo -e "${YELLOW}防火墙已开放 80 端口${NC}"
fi

echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}✅ Ubuntu 24.04 部署完成！${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "访问地址: http://$SERVER_IP"
echo -e "项目路径: $APP_DIR"
echo -e "\n${YELLOW}常用命令：${NC}"
echo -e "查看服务状态: sudo systemctl status material-system"
echo -e "重启服务: sudo systemctl restart material-system"
echo -e "查看日志: journalctl -u material-system -f"
echo -e "查看 Django 日志: tail -f $APP_DIR/logs/django.log"
echo -e "\n${GREEN}如有问题，检查：${NC}"
echo -e "1. Nginx 配置: sudo nginx -t"
echo -e "2. 服务状态: sudo systemctl status material-system nginx"
echo -e "3. 防火墙: sudo ufw status"
