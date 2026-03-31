# 数据库备份指南

## 📋 概述

系统提供自动化的数据库备份机制，支持定时备份和手动备份。

## 🔧 备份脚本

位置：`scripts/backup_db.sh`

### 功能特性
- ✅ 自动创建带时间戳的备份文件
- ✅ 压缩备份以节省空间
- ✅ 自动清理过期备份
- ✅ 显示备份统计信息
- ✅ 安全的文件复制（避免锁表）

### 手动备份

```bash
# 进入项目目录
cd /home/abc/Project-Material-Management-System

# 执行备份（默认保留 30 天）
bash scripts/backup_db.sh

# 或指定保留天数
bash scripts/backup_db.sh 60  # 保留 60 天
```

### 备份文件位置
```
backups/
├── db-20260324-020000.sqlite3.gz  # 每日备份
├── db-20260325-020000.sqlite3.gz
└── ...
```

## ⏰ 定时备份配置

### 方案一：使用 crontab（推荐）

#### 1. 编辑 crontab
```bash
crontab -e
```

#### 2. 添加定时任务

**每天凌晨 2 点备份（保留 30 天）：**
```bash
0 2 * * * cd /home/abc/Project-Material-Management-System && bash scripts/backup_db.sh 30 >> logs/backup.log 2>&1
```

**每周日早上 3 点备份（保留 90 天）：**
```bash
0 3 * * 0 cd /home/abc/Project-Material-Management-System && bash scripts/backup_db.sh 90 >> logs/backup_weekly.log 2>&1
```

#### 3. 验证 crontab
```bash
# 查看当前 crontab 配置
crontab -l

# 检查 cron 服务状态
systemctl status cron
```

### 方案二：使用提供的示例文件

```bash
# 直接应用示例配置
crontab /home/abc/Project-Material-Management-System/scripts/backup_crontab.example

# 验证配置
crontab -l
```

## 📊 日志查看

### 备份日志
```bash
# 查看最近的备份日志
tail -f logs/backup.log

# 查看所有备份记录
cat logs/backup.log

# 按日期查看
grep "2026-03" logs/backup.log
```

### 备份统计
```bash
# 查看备份文件数量
ls -lh backups/db-*.sqlite3.gz | wc -l

# 查看备份总大小
du -sh backups/

# 查看最近的备份
ls -lht backups/db-*.sqlite3.gz | head -5
```

## 🔄 恢复数据库

### 从备份恢复
```bash
# 1. 停止 Django 服务（如果正在运行）
# Ctrl+C 停止 runserver

# 2. 解压备份文件
gunzip -k backups/db-20260324-020000.sqlite3.gz

# 3. 恢复数据库
cp backups/db-20260324-020000.sqlite3 db.sqlite3

# 4. 重启服务
python manage.py runserver
```

### 恢复特定日期的数据
```bash
# 列出所有可用备份
ls -lh backups/

# 选择需要的日期，解压并恢复
gunzip -k backups/db-YYYYMMDD-HHMMSS.sqlite3.gz
cp backups/db-YYYYMMDD-HHMMSS.sqlite3 db.sqlite3
```

## ⚙️ 高级配置

### 修改备份保留策略

编辑 crontab，调整保留天数：
```bash
# 每日备份保留 7 天
0 2 * * * bash scripts/backup_db.sh 7

# 每周备份保留 180 天
0 3 * * 0 bash scripts/backup_db.sh 180
```

### 备份到其他位置

修改 `scripts/backup_db.sh` 中的 BACKUP_DIR：
```bash
BACKUP_DIR="/mnt/external_drive/backups"
```

### 远程备份

添加 rsync 同步到远程服务器：
```bash
# 在 backup_db.sh 末尾添加
rsync -avz "$BACKUP_DIR" user@remote:/backup/location/
```

## 🛡️ 最佳实践

1. **多重备份策略**
   - 每日备份：保留 7-30 天
   - 每周备份：保留 1-3 个月
   - 每月备份：保留 6-12 个月

2. **异地备份**
   - 定期将备份复制到外部存储
   - 使用云存储服务

3. **定期检查**
   - 每周检查备份日志
   - 每月测试恢复流程

4. **监控告警**
   - 设置备份失败告警
   - 监控磁盘空间

## ❓ 故障排查

### 备份失败
```bash
# 检查日志
tail -50 logs/backup.log

# 检查磁盘空间
df -h

# 检查脚本权限
chmod +x scripts/backup_db.sh
```

### Cron 未执行
```bash
# 检查 cron 服务
systemctl status cron

# 启动 cron
sudo systemctl start cron

# 启用开机自启
sudo systemctl enable cron
```

### 备份文件损坏
```bash
# 测试备份文件完整性
gunzip -t backups/db-*.sqlite3.gz

# 如果有错误，使用上一个可用备份
```

## 📞 相关文档

- [部署文档](deploy/README.md)
- [快速开始](docs/QUICK_START.md)
