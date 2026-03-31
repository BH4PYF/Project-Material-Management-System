# 定时备份 - 快速开始

## 🚀 一键设置（推荐）

```bash
cd /home/abc/Project-Material-Management-System
bash scripts/setup_cron_backup.sh
```

按照提示选择备份策略即可！

## 📋 手动设置

### 方案 1：使用 crontab 命令

```bash
# 编辑 crontab
crontab -e

# 添加以下内容（每天凌晨 2 点备份）
0 2 * * * cd /home/abc/Project-Material-Management-System && bash scripts/backup_db.sh 30 >> logs/backup.log 2>&1
```

### 方案 2：应用示例配置

```bash
# 直接应用预设的配置文件
crontab scripts/backup_crontab.example
```

## 🔍 验证设置

```bash
# 查看当前 crontab
crontab -l

# 检查 cron 服务
systemctl status cron
```

## 📊 日常管理

### 手动备份
```bash
bash scripts/backup_db.sh
```

### 查看备份日志
```bash
tail -f logs/backup.log
```

### 查看备份文件
```bash
ls -lh backups/
```

### 恢复数据库
```bash
# 解压备份
gunzip -k backups/db-20260324-020000.sqlite3.gz

# 替换数据库
cp backups/db-20260324-020000.sqlite3 db.sqlite3
```

## ❌ 移除定时备份

```bash
# 编辑 crontab，删除备份任务行
crontab -e
```

---

📖 详细文档：[DATABASE_BACKUP_GUIDE.md](DATABASE_BACKUP_GUIDE.md)
