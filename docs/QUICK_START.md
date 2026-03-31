# 材料管理系统 快速部署指南

## 🚀 一键部署

### Ubuntu 24.04 (推荐)
```bash
sudo bash deploy/ubuntu/deploy_ubuntu_24.sh
```

### Ubuntu 20.04/22.04
```bash
sudo bash deploy/ubuntu/deploy_ubuntu_20_22.sh
```

## 📋 部署前准备

### 系统要求
- Ubuntu 20.04 / 22.04 / 24.04
- 至少 1GB 内存
- 至少 10GB 磁盘空间
- root 权限或 sudo 权限

### 网络要求
- 开放端口：80 (HTTP), 22 (SSH)
- 可访问互联网（下载安装包）

## 📝 部署流程

脚本将自动完成：

1. ✅ 系统更新和依赖安装
2. ✅ Python 虚拟环境创建
3. ✅ 项目代码部署
4. ✅ 数据库初始化
5. ✅ Gunicorn 服务配置
6. ✅ Nginx 反向代理配置
7. ✅ 防火墙设置

## 🔍 部署后检查

### 1. 查看服务状态
```bash
sudo systemctl status material-system
```

### 2. 访问系统
在浏览器中输入服务器IP：
```
http://你的服务器IP
```

### 3. 登录系统
- 使用创建的管理员账号登录
- 默认地址：`http://IP/admin`

## 🔧 常用命令

### 重启服务
```bash
sudo systemctl restart material-system
```

### 查看日志
```bash
# 服务日志
journalctl -u material-system -f

# Django 日志
tail -f ~/material-system/logs/django.log
```

### 备份数据库
```bash
./scripts/backup_db.sh
```

## 📚 详细文档

- 完整说明：`README_MATERIAL_SYSTEM.md`
- 部署详解：`deploy/ubuntu/README.md`
- 项目整理：`PROJECT_CLEANUP_LOG.md`

## ⚠️ 注意事项

1. **首次部署**需要约 5-10 分钟
2. 部署过程中会提示创建管理员账号
3. 部署完成后请妥善保管管理员密码
4. 建议定期备份数据库

## 💡 技术支持

遇到问题请查看：
- 系统日志：`journalctl -u material-system`
- Django 日志：`logs/django.log`
- Nginx 日志：`/var/log/nginx/error.log`

---

**版本**: v1.8  
**更新日期**: 2026-03-22
