# 材料管理系统 V1.10

[![Django](https://img.shields.io/badge/Django-6.0.3-green)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.12-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

专业的工程项目材料管理系统，用于管理项目中的材料采购、入库、发货、成本分析和统计报表。

## 功能特性

### 基础管理
- **材料管理**：材料的增删改查、分类管理（支持自定义分类、重复名称校验）
- **项目管理**：项目信息管理、项目成本统计、状态跟踪
- **供应商管理**：供应商信息维护、信用评级、采购记录查询
- **用户管理**：多角色权限控制（管理员/物资部/材料员/供应商）

### 采购、发货与入库管理
- **采购计划**：采购计划制定、审批流程、状态跟踪、批量导出
- **发货管理**：发货单创建、物流跟踪、批量导出
- **快速收货**：极简收货流程、自动填充信息
- **入库管理**：材料入库登记、Excel 导出、批次管理

### 统计分析
- **统计报表**：项目成本分析、供应商采购排名、月度统计
- **图表分析**：入库总额 TOP10 柱状图、入库大类分布饼图，支持日期范围筛选
- **操作日志**：完整的审计日志、操作追踪
- **Excel 导出**：总采购量入出记录、采购计划、发货单导出

### 系统管理
- **系统设置**：导航栏标题定制、材料分类管理、登录限流配置
- **权限控制**：基于角色的访问控制
- **数据备份**：定时自动备份、手动备份支持、备份恢复
- **性能监控**：API 性能统计、慢请求追踪

## 快速开始

### 环境要求
- Python 3.10+
- pip
- Git (可选)
- SQLite (开发环境) / MySQL (生产环境)

### 安装步骤

#### 1. 获取项目
```bash
git clone https://github.com/BH4PYF/Project-Material-Management-System.git
cd Project-Material-Management-System
```

#### 2. 创建虚拟环境
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

#### 3. 安装依赖
```bash
pip install -r requirements.txt
```

#### 4. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 文件修改配置（特别是 SECRET_KEY）
```

#### 5. 初始化数据库
```bash
python manage.py migrate
python manage.py createsuperuser  # 创建管理员账号
```

#### 6. 运行开发服务器
```bash
python manage.py runserver
```
访问 http://127.0.0.1:8000/

## 浏览器支持

- Chrome (推荐)
- Firefox
- Safari
- Edge

## 部署到生产环境

### Ubuntu 部署（推荐）

#### Ubuntu 24.04（推荐）
```bash
sudo bash deploy/ubuntu/deploy_ubuntu_24.sh
```

#### Ubuntu 20.04/22.04
```bash
sudo bash deploy/ubuntu/deploy_ubuntu.sh
```

### CentOS 7 部署
```bash
cd deploy/centos7
sudo bash deploy.sh
```

详细部署说明请参考各部署目录下的 README.md 文件。

## 项目结构

```
Project-Material-Management-System/
├── deploy/                     # 部署脚本目录
│   ├── centos7/               # CentOS 7 部署脚本
│   └── ubuntu/                # Ubuntu 部署脚本
├── inventory/                  # 主应用
│   ├── management/commands/   # 自定义管理命令
│   ├── migrations/            # 数据库迁移
│   ├── templatetags/          # 模板标签
│   ├── views/                 # 视图函数（按功能模块拆分）
│   │   ├── auth.py            # 登录/登出
│   │   ├── dashboard.py       # 仪表盘
│   │   ├── delivery.py        # 发货管理
│   │   ├── export.py          # Excel 导入导出
│   │   ├── inbound.py         # 入库管理
│   │   ├── material.py        # 材料管理
│   │   ├── performance.py     # 性能监控
│   │   ├── project.py         # 项目管理
│   │   ├── purchase_plan.py   # 采购计划
│   │   ├── report.py          # 统计报表与图表分析
│   │   ├── settings.py        # 系统设置
│   │   ├── supplier.py        # 供应商管理
│   │   └── utils.py           # 工具函数
│   ├── models.py              # 数据模型（含软删除基础设施）
│   ├── urls.py                # URL 路由
│   ├── admin.py               # Admin 配置
│   ├── context_processors.py  # 上下文处理器
│   └── tests.py               # 单元测试
├── material_system/           # Django 项目配置
│   ├── settings.py            # 基础配置
│   ├── urls.py                # 根路由
│   ├── wsgi.py                # WSGI 配置
│   └── asgi.py                # ASGI 配置
├── scripts/                   # 工具脚本
│   ├── backup_db.sh           # 数据库备份脚本
│   ├── setup_cron_backup.sh   # 定时备份配置
│   └── reset_database.sh      # 数据库重置脚本
├── static/                    # 静态文件
│   ├── css/                   # 样式文件
│   ├── js/                    # JavaScript 文件
│   └── vendor/                # 第三方库（Bootstrap 等）
├── templates/                 # HTML 模板
│   ├── base.html              # 基础模板
│   ├── login.html             # 登录页面
│   └── inventory/             # 业务模块模板
├── docs/                      # 项目文档
├── logs/                      # 日志文件
├── backups/                   # 数据库备份
├── .env.example               # 环境变量示例
├── manage.py                  # Django 管理脚本
├── requirements.txt           # Python 依赖
└── pytest.ini                 # Pytest 配置
```

## 数据库备份

### 定时备份设置（推荐）

```bash
# 一键设置定时备份（交互式）
bash scripts/setup_cron_backup.sh

# 或手动配置 crontab
crontab -e
# 添加：每天凌晨 2 点自动备份
0 2 * * * cd /path/to/Project-Material-Management-System && bash scripts/backup_db.sh 30 >> logs/backup.log 2>&1
```

### 手动备份

```bash
# 手动触发备份
bash scripts/backup_db.sh [保留天数]
```

备份文件保存在 `backups/` 目录，自动压缩，默认保留 30 天。

详细文档请参考：[数据库备份指南](docs/DATABASE_BACKUP_GUIDE.md)

## 主要功能模块

### 1. 仪表盘
- 今日入库记录展示
- 项目/材料/供应商概览

### 2. 项目管理
- 项目信息维护、状态跟踪（进行中/已完工/暂停）
- 项目成本统计
- 支持 Excel 导入导出

### 3. 材料管理
- 材料档案维护、材料分类管理
- 支持 Excel 导入导出

### 4. 供应商管理
- 供应商信息维护、信用评级（优秀/良好/一般）
- 采购记录查询
- 支持 Excel 导入导出

### 5. 采购计划
- 采购计划制定、状态跟踪（审批中/采购中/发货中/已入库）
- 批量导入导出、预计金额计算

### 6. 发货管理
- 发货单创建、物流跟踪（专车/物流）
- 车牌号/运单号记录、二维码生成
- 批量导入导出

### 7. 快速收货
- 扫码收货功能、极简收货流程、自动填充信息

### 8. 入库管理
- 入库登记、质量验收、批次管理
- 支持 Excel 导入导出

### 9. 统计报表
- 项目成本分析、供应商采购排名、月度统计报表

### 10. 图表分析
- 入库总额 TOP10 柱状图
- 入库大类分布饼图
- 支持日期范围筛选

### 11. 系统管理
- 用户管理、角色权限配置
- 系统设置（导航栏标题、登录限流）
- 材料分类管理（自定义分类、重复名称校验）
- 数据备份与恢复、操作日志查询
- 性能监控仪表盘

## 安全配置

生产环境部署前必须修改：

1. **生成新密钥**
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(50))"
   ```
   将输出粘贴到 `.env` 的 `SECRET_KEY`

2. **关闭调试模式**
   在 `.env` 中设置 `DEBUG=False`

3. **限制允许的主机**
   在 `.env` 中设置 `ALLOWED_HOSTS=你的域名或IP`

## 日志

日志文件位于 `logs/django.log`，记录系统运行信息和错误。

## 测试

```bash
# 运行所有测试
python manage.py test inventory

# 或使用 pytest（需要先安装）
pytest

# 带覆盖率报告
pytest --cov=inventory --cov-report=html
```

## 更新日志

### v1.10 (2026-03-31)
- 修复用户编辑成功提示从横幅改成模态框的问题
- 修改编辑模态框中的角色分组选择，从调用用户分组数据改为调用角色数据
- 清理无用的文件和代码
- 优化项目目录结构

### v1.9 (2026-03-26)
- 图表分析页面优化：移除月度入库趋势，保留入库 TOP10 和大类分布图
- 系统设置页面操作提示统一为模态框（替代横幅提示）
- 材料分类删除改用模态框确认（替代浏览器原生 confirm）
- 材料分类添加增加重复名称校验
- 修复软删除记录导致分类编码冲突的问题（generate_code 改用 all_objects）
- 清理无用导入和冗余文档

### v1.8 (2026-03-22)
- 新增发货管理批量导入导出功能
- 导航栏标题可定制化配置
- 首页仅展示今日入库记录
- 侧边栏 UI 优化
- 系统设置增加公司/项目名称配置
- 字体大小优化，提升可读性
- 导入模板下载功能完善

### v1.7
- 快速收货页面极简重构
- 移除验收人与质量状态字段
- 自动填充收货日期和项目地址
- 列表同步机制优化

### v1.6
- 发货管理批量导出功能
- 项目采购分析成本占比优化

### v1.5
- 入库管理列表导入导出优化
- 单位列显示优化
- 数据一致性增强

---

## 文档

更多详细信息请查看 [docs](docs/) 目录：
- [快速开始指南](docs/QUICK_START.md)
- [数据库备份指南](docs/DATABASE_BACKUP_GUIDE.md)

---

## 贡献

欢迎提交 Issue 或 Pull Request。

## 许可证

[MIT License](LICENSE)

## 联系方式

项目维护者：妞妞爸
