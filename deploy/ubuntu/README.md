# Ubuntu 部署脚本说明

本目录包含适用于 Ubuntu 系统的一键部署脚本。

## 📋 版本说明

### deploy_ubuntu_20_22.sh
- **适用系统**: Ubuntu 20.04 / Ubuntu 22.04
- **功能**: 完整的自动化部署脚本
- **依赖**: Python 3, Nginx, Redis, Gunicorn

### deploy_ubuntu_24.sh  
- **适用系统**: Ubuntu 24.04 (推荐)
- **功能**: 针对 Ubuntu 24.04 优化的部署脚本
- **改进**: 支持最新的系统包和配置

## 🚀 使用方法

### Ubuntu 20.04/22.04
```bash
sudo bash deploy/ubuntu/deploy_ubuntu_20_22.sh
```

### Ubuntu 24.04 (推荐)
```bash
sudo bash deploy/ubuntu/deploy_ubuntu_24.sh
```

## 📝 部署流程

脚本会自动完成以下操作：

1. **系统更新** - 更新系统包并安装必要依赖
2. **项目配置** - 创建项目目录，复制或克隆代码
3. **环境搭建** - 创建 Python 虚拟环境并安装依赖
4. **数据库初始化** - 执行迁移、收集静态文件
5. **服务配置** - 配置 Gunicorn 系统服务
6. **Nginx 配置** - 配置反向代理
7. **防火墙设置** - 开放必要的端口

## ⚙️ 部署后检查

### 1. 检查服务状态
```bash
sudo systemctl status material-system
```

### 2. 查看日志
```bash
# Gunicorn 服务日志
journalctl -u material-system -f

# Django 应用日志
tail -f ~/material-system/logs/django.log
```

### 3. 测试访问
在浏览器中访问服务器 IP 地址：
```
http://你的服务器IP
```

## 🔧 常用运维命令

### 重启服务
```bash
sudo systemctl restart material-system
```

### 停止服务
```bash
sudo systemctl stop material-system
```

### 启动服务
```bash
sudo systemctl start material-system
```

### 开机自启
```bash
sudo systemctl enable material-system
```

### 修改配置后重载
```bash
sudo systemctl daemon-reload
sudo systemctl restart material-system
```

## 📊 系统架构

```
用户请求
    ↓
Nginx (80 端口)
    ↓
Gunicorn Socket
    ↓
Django 应用
    ↓
SQLite/MySQL 数据库
```

## 🔐 安全建议

1. **修改密钥**: 部署后自动生成新的 SECRET_KEY
2. **关闭调试**: 生产环境 DEBUG=False
3. **限制主机**: 配置 ALLOWED_HOSTS 为实际域名/IP
4. **HTTPS**: 建议使用 Certbot 配置 SSL 证书
5. **防火墙**: 仅开放必要的端口（80, 443, 22）

## 💾 数据备份

自动备份脚本位于 `scripts/backup_db.sh`，每天凌晨 2 点执行。

手动备份：
```bash
./scripts/backup_db.sh
```

备份文件保存在 `backups/` 目录，保留 30 天。

## ❓ 故障排查

### 问题 1: 服务无法启动
```bash
# 查看详细错误
journalctl -u material-system -n 50 --no-pager

# 检查 Python 依赖
source venv/bin/activate
pip install -r requirements.txt
```

### 问题 2: Nginx 无法访问
```bash
# 检查 Nginx 配置
sudo nginx -t

# 重启 Nginx
sudo systemctl restart nginx
```

### 问题 3: 权限问题
```bash
# 修复项目目录权限
sudo chown -R $USER:$USER ~/material-system
```

## 📞 技术支持

如有问题，请查看：
- Django 日志：`~/material-system/logs/django.log`
- 系统日志：`journalctl -u material-system -f`
- Nginx 日志：`/var/log/nginx/error.log`

---

**最后更新**: 2026-03-22
**版本**: v1.8
