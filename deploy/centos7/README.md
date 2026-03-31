# 材料管理系统 CentOS 7 部署指南

## 系统要求
- CentOS 7.x
- Python 3.8+
- 512MB RAM minimum
- 1GB disk space

## 部署步骤

### 1. 系统准备
```bash
# 更新系统
sudo yum update -y

# 安装基础依赖
sudo yum install -y epel-release
sudo yum install -y python3 python3-pip python3-devel gcc gcc-c++ make
sudo yum install -y sqlite-devel
```

### 2. 创建部署用户
```bash
# 创建专用用户
sudo useradd -m -s /bin/bash django
sudo passwd django

# 切换到django用户
sudo su - django
```

### 3. 部署应用
```bash
# 克隆或复制项目文件到服务器
# 假设项目在 /home/django/material_system

# 安装Python依赖
cd /home/django/material_system
pip3 install --user -r requirements.txt

# 安装pysqlite3解决版本兼容性问题
pip3 install --user pysqlite3

# 设置环境变量
export DJANGO_SETTINGS_MODULE=material_system.settings
```

### 4. 数据库初始化
```bash
# 应用数据库迁移
python3 manage.py migrate

# 创建管理员用户
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@example.com', 'Liyifeiniuniu1027-')" | python3 manage.py shell
```

### 5. 生产环境配置
```bash
# 收集静态文件
python3 manage.py collectstatic --noinput

# 设置生产环境变量
export DJANGO_SETTINGS_MODULE=material_system.settings
export DEBUG=False
```

## 启动方式

### 方式1：使用Gunicorn（推荐）
```bash
# 安装Gunicorn
pip3 install --user gunicorn

# 启动服务
gunicorn material_system.wsgi:application --bind 0.0.0.0:8000 --workers 3
```

### 方式2：使用Systemd服务
```bash
# 创建systemd服务文件
sudo tee /etc/systemd/system/material-system.service << EOF
[Unit]
Description=Material Management System
After=network.target

[Service]
Type=simple
User=django
WorkingDirectory=/home/django/material_system
Environment=PATH=/home/django/.local/bin
Environment=DJANGO_SETTINGS_MODULE=material_system.settings
ExecStart=/home/django/.local/bin/gunicorn material_system.wsgi:application --bind 0.0.0.0:8000 --workers 3
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# 启用并启动服务
sudo systemctl daemon-reload
sudo systemctl enable material-system
sudo systemctl start material-system
```

### 方式3：使用Nginx反向代理
```bash
# 安装Nginx
sudo yum install -y nginx

# 配置Nginx
sudo tee /etc/nginx/conf.d/material-system.conf << EOF
server {
    listen 80;
    server_name your-domain.com;

    location /static/ {
        alias /home/django/material_system/staticfiles/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# 启动Nginx
sudo systemctl enable nginx
sudo systemctl start nginx
```

## 防火墙配置
```bash
# 开放端口
sudo firewall-cmd --permanent --add-port=80/tcp
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --reload
```

## 监控和日志
```bash
# 查看服务状态
sudo systemctl status material-system

# 查看日志
sudo journalctl -u material-system -f

# 应用日志位置
# /home/django/material_system/logs/
```

## 备份策略
```bash
# 数据库备份脚本
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/home/django/backups"
mkdir -p $BACKUP_DIR

# 备份SQLite数据库
cp /home/django/material_system/db.sqlite3 $BACKUP_DIR/db_backup_$DATE.sqlite3

# 备份媒体文件
tar -czf $BACKUP_DIR/media_backup_$DATE.tar.gz /home/django/material_system/media/
```

## 故障排除
1. 检查服务状态：`systemctl status material-system`
2. 查看日志：`journalctl -u material-system`
3. 验证端口监听：`netstat -tlnp | grep :8000`
4. 测试数据库连接：`python3 manage.py dbshell`

## 安全建议
- 定期更新系统和依赖包
- 使用HTTPS（通过Let's Encrypt）
- 设置适当的文件权限
- 定期备份数据
- 监控系统资源使用情况