#!/bin/bash
# 创建CentOS 7部署包

DEPLOY_DIR="deploy/centos7"
PACKAGE_NAME="material_system_centos7_deploy_$(date +%Y%m%d_%H%M%S)"
PACKAGE_FILE="${PACKAGE_NAME}.tar.gz"

echo "创建部署包: $PACKAGE_FILE"

# 创建临时目录
TEMP_DIR="/tmp/${PACKAGE_NAME}"
mkdir -p "$TEMP_DIR"

# 复制部署文件
cp -r "$DEPLOY_DIR"/* "$TEMP_DIR/"

# 复制项目核心文件
cp -r material_system "$TEMP_DIR/"
cp -r inventory "$TEMP_DIR/"
cp -r templates "$TEMP_DIR/"
cp -r static "$TEMP_DIR/"
cp manage.py "$TEMP_DIR/"
cp requirements.txt "$TEMP_DIR/"

# 创建安装说明
cat > "$TEMP_DIR/INSTALL.md" << 'EOF'
# 材料管理系统 CentOS 7 部署包

## 包含文件说明

### 部署脚本
- `deploy.sh` - 自动部署脚本
- `backup.sh` - 备份恢复脚本
- `monitor.sh` - 系统监控脚本

### 配置文件
- `material-system.service` - systemd服务配置
- `nginx.conf` - Nginx配置文件
- `README.md` - 详细部署文档
- `deployment_checklist.md` - 部署检查清单

### 应用文件
- `material_system/` - Django项目配置
- `inventory/` - 应用模块
- `templates/` - 模板文件
- `static/` - 静态文件
- `manage.py` - Django管理脚本
- `requirements.txt` - Python依赖

## 部署步骤

### 快速部署（推荐）
```bash
# 1. 解压部署包
tar -xzf material_system_centos7_deploy_*.tar.gz
cd material_system_centos7_deploy_*

# 2. 运行自动部署脚本
chmod +x deploy.sh
sudo ./deploy.sh
```

### 手动部署
请参考 `README.md` 文件中的详细步骤。

## 系统要求
- CentOS 7.x
- Python 3.8+
- 512MB RAM minimum
- 1GB disk space

## 访问信息
- 应用地址: http://your-server-ip/
- 管理后台: http://your-server-ip/admin/
- 默认账号: admin
- 默认密码: Liyifeiniuniu1027-

## 注意事项
1. 部署前请确保系统满足最低要求
2. 建议在部署前备份现有数据
3. 部署过程中需要root权限
4. 部署完成后请修改默认密码
5. 建议配置SSL证书以启用HTTPS

## 技术支持
如有问题请联系系统管理员。
EOF

# 创建版本信息文件
cat > "$TEMP_DIR/VERSION" << EOF
材料管理系统 CentOS 7 部署包
版本: 1.0.0
打包时间: $(date)
Django版本: 6.0.2
Python要求: 3.8+
EOF

# 创建压缩包
tar -czf "$PACKAGE_FILE" -C /tmp "$PACKAGE_NAME"

# 移动到当前目录
mv "$PACKAGE_FILE" .

# 清理临时文件
rm -rf "$TEMP_DIR"

echo "部署包创建完成: $PACKAGE_FILE"
echo "文件大小: $(du -h "$PACKAGE_FILE" | cut -f1)"