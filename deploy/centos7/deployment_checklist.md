# 材料管理系统 CentOS 7 部署清单

## 部署前检查清单

### ✅ 系统环境检查
- [ ] CentOS 7.x 系统版本
- [ ] 至少 512MB RAM
- [ ] 至少 1GB 可用磁盘空间
- [ ] 网络连接正常
- [ ] 防火墙服务可用

### ✅ 依赖安装检查
- [ ] EPEL 源已安装
- [ ] Python 3.8+ 已安装
- [ ] pip3 可用
- [ ] gcc gcc-c++ make 已安装
- [ ] sqlite-devel 已安装
- [ ] nginx 已安装

### ✅ 用户和权限检查
- [ ] django 用户已创建
- [ ] django 用户有 sudo 权限
- [ ] 项目目录权限正确设置
- [ ] 日志目录可写

### ✅ 应用配置检查
- [ ] 项目文件完整上传
- [ ] requirements.txt 依赖包可安装
- [ ] settings.py 配置正确
- [ ] 数据库配置正确
- [ ] 静态文件目录存在

## 部署步骤验证清单

### 🔧 系统配置
- [ ] 系统更新完成
- [ ] 依赖包安装完成
- [ ] 部署用户创建完成
- [ ] 项目目录结构正确

### 🐍 Python环境配置
- [ ] Python依赖安装完成
- [ ] pysqlite3 安装成功
- [ ] gunicorn 安装成功
- [ ] 环境变量设置正确

### 🗄️ 数据库配置
- [ ] 数据库迁移完成
- [ ] 管理员用户创建成功
- [ ] 静态文件收集完成
- [ ] 媒体文件目录创建

### ⚙️ 服务配置
- [ ] systemd 服务文件部署
- [ ] nginx 配置文件部署
- [ ] 防火墙规则配置
- [ ] 服务开机自启设置

### 🚀 服务启动验证
- [ ] Django 服务启动成功
- [ ] nginx 服务启动成功
- [ ] 端口监听正常
- [ ] HTTP 响应正常
- [ ] 管理后台可访问

## 生产环境检查清单

### 🔒 安全配置
- [ ] DEBUG=False 设置
- [ ] SECRET_KEY 已修改
- [ ] 防火墙规则正确
- [ ] SSL/HTTPS 配置（如需要）
- [ ] 定期备份策略设置

### 📊 监控配置
- [ ] 监控脚本部署
- [ ] 日志轮转配置
- [ ] 告警机制设置
- [ ] 性能监控启用

### 🔄 运维配置
- [ ] 备份脚本部署
- [ ] 自动更新机制
- [ ] 故障恢复流程
- [ ] 文档和操作手册

## 常用管理命令

### 服务管理
```bash
# 启动服务
sudo systemctl start material-system
sudo systemctl start nginx

# 停止服务
sudo systemctl stop material-system
sudo systemctl stop nginx

# 重启服务
sudo systemctl restart material-system
sudo systemctl restart nginx

# 查看服务状态
sudo systemctl status material-system
sudo systemctl status nginx
```

### 日志查看
```bash
# 应用日志
sudo journalctl -u material-system -f

# Nginx日志
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# 系统监控日志
tail -f /home/django/backups/monitor.log
```

### 备份恢复
```bash
# 执行备份
/home/django/material_system/deploy/centos7/backup.sh backup

# 列出备份
/home/django/material_system/deploy/centos7/backup.sh list

# 恢复备份
/home/django/material_system/deploy/centos7/backup.sh restore <时间戳>
```

### 监控检查
```bash
# 执行监控检查
/home/django/material_system/deploy/centos7/monitor.sh check

# 查看系统信息
/home/django/material_system/deploy/centos7/monitor.sh info

# 重启服务
/home/django/material_system/deploy/centos7/monitor.sh restart
```

## 故障排除清单

### 常见问题
- [ ] 服务无法启动 → 检查日志和依赖
- [ ] 端口无法访问 → 检查防火墙和配置
- [ ] 数据库连接失败 → 检查数据库文件和权限
- [ ] 静态文件404 → 检查collectstatic和nginx配置
- [ ] 内存/CPU占用过高 → 检查监控和优化配置

### 应急处理
1. 立即检查服务状态
2. 查看相关日志文件
3. 尝试重启服务
4. 如问题持续，执行备份恢复
5. 联系技术支持

## 部署完成确认

### ✅ 部署成功标准
- [ ] 应用可通过浏览器正常访问
- [ ] 管理后台登录正常
- [ ] 所有核心功能可正常使用
- [ ] 监控告警机制正常工作
- [ ] 备份策略已生效
- [ ] 文档和操作手册完整

### 📋 交付物清单
- [ ] 部署文档
- [ ] 操作手册
- [ ] 监控配置
- [ ] 备份策略
- [ ] 应急预案
- [ ] 联系方式和支持信息

---
**部署完成时间**: ___________  
**部署人员**: ___________  
**验收人员**: ___________