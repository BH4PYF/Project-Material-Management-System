#!/bin/bash
# 快速重置数据库并生成测试数据的脚本
# 使用方法：./scripts/reset_database.sh

set -e  # 遇到错误立即退出

echo "============================================================"
echo "🗑️  开始重置数据库..."
echo "============================================================"

# 1. 删除数据库文件
echo "📁 删除旧数据库文件..."
rm -f db.sqlite3

# 2. 重新迁移
echo "🔄 执行数据库迁移..."
python3 manage.py migrate

# 3. 创建缓存表（重要！）
echo "💾 创建缓存表..."
python3 manage.py createcachetable

# 4. 生成测试数据
echo "✨ 生成测试数据..."
python3 manage.py shell << 'EOF'
from django.contrib.auth.models import User
from inventory.models import Profile, Project, Category, Material, Supplier
from decimal import Decimal

print('\n=== 创建管理员账户 ===')
admin_user = User.objects.filter(username='admin').first()
if not admin_user:
    admin_user = User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    Profile.objects.get_or_create(user=admin_user, defaults={'role': 'admin'})
    print('✓ 管理员账户已创建：admin / admin123')
else:
    print('✓ 管理员账户已存在')

print('\n=== 创建材料分类 ===')
categories_data = [
    ('CAT001', '钢材', '建筑用钢材'),
    ('CAT002', '水泥', '普通硅酸盐水泥'),
    ('CAT003', '混凝土', '商品混凝土'),
]
for code, name, remark in categories_data:
    Category.objects.get_or_create(code=code, defaults={'name': name, 'remark': remark})
print(f'✓ 已创建 {Category.objects.count()} 个材料分类')

print('\n=== 创建项目 ===')
projects_data = [
    ('PRJ001', '科技创新园一期工程', '张工程师', '北京市朝阳区', '2024-01-01', '2025-12-31', 50000000, 'active'),
    ('PRJ002', '地铁 5 号线站点建设', '李工程师', '北京市海淀区', '2024-03-01', '2026-02-28', 80000000, 'active'),
    ('PRJ003', '商业中心综合体', '王工程师', '上海市浦东新区', '2024-06-01', '2026-05-31', 120000000, 'active'),
    ('PRJ004', '住宅小区二期', '赵工程师', '广州市天河区', '2024-09-01', '2026-08-31', 60000000, 'planning'),
]
for code, name, manager, location, start, end, budget, status in projects_data:
    Project.objects.get_or_create(code=code, defaults={
        'name': name, 'manager': manager, 'location': location,
        'start_date': start, 'end_date': end, 'budget': budget, 'status': status
    })
print(f'✓ 已创建 {Project.objects.count()} 个项目')

print('\n=== 创建供应商 ===')
suppliers_data = [
    ('SUP001', '华东钢铁有限公司', '陈经理', '13800138001', '上海市宝山区', 'AAA', '2020-01-01'),
    ('SUP002', '北方水泥集团', '刘经理', '13800138002', '河北省唐山市', 'AA', '2019-06-01'),
    ('SUP003', '华南建材供应公司', '黄经理', '13800138003', '广东省深圳市', 'AAA', '2021-03-01'),
    ('SUP004', '西南混凝土厂', '周经理', '13800138004', '四川省成都市', 'A', '2022-01-01'),
]
for code, name, contact, phone, address, credit, date in suppliers_data:
    Supplier.objects.get_or_create(code=code, defaults={
        'name': name, 'contact': contact, 'phone': phone,
        'address': address, 'credit_rating': credit, 'start_date': date
    })
print(f'✓ 已创建 {Supplier.objects.count()} 个供应商')

print('\n=== 创建材料 ===')
cat1 = Category.objects.get(code='CAT001')
cat2 = Category.objects.get(code='CAT002')
cat3 = Category.objects.get(code='CAT003')

materials_data = [
    ('MAT001', '螺纹钢 HRB400', cat1, 'Φ12mm', '吨', Decimal('4200.00'), 100),
    ('MAT002', '盘螺 HRB400', cat1, 'Φ8mm', '吨', Decimal('4350.00'), 80),
    ('MAT003', '线材 HPB300', cat1, 'Φ6.5mm', '吨', Decimal('4100.00'), 60),
    ('MAT004', '普通硅酸盐水泥 P.O 42.5', cat2, '袋装 50kg', '吨', Decimal('450.00'), 200),
    ('MAT005', '复合硅酸盐水泥 P.C 32.5', cat2, '袋装 50kg', '吨', Decimal('380.00'), 150),
    ('MAT006', 'C30 商品混凝土', cat3, '立方米', '立方米', Decimal('420.00'), 500),
    ('MAT007', 'C35 商品混凝土', cat3, '立方米', '立方米', Decimal('450.00'), 400),
]
for code, name, category, spec, unit, price, stock in materials_data:
    Material.objects.get_or_create(code=code, defaults={
        'name': name, 'category': category, 'spec': spec,
        'unit': unit, 'standard_price': price, 'safety_stock': stock
    })
print(f'✓ 已创建 {Material.objects.count()} 个材料')

print('\n✅ 基础数据生成完成！')
EOF

echo ""
echo "============================================================"
echo "✅ 数据库重置完成！"
echo "============================================================"
echo ""
echo "📊 数据统计："
python3 manage.py shell -c "
from inventory.models import Category, Project, Supplier, Material
print(f'  - 材料分类：{Category.objects.count()} 个')
print(f'  - 项目：{Project.objects.count()} 个')
print(f'  - 供应商：{Supplier.objects.count()} 个')
print(f'  - 材料：{Material.objects.count()} 个')
"
echo ""
echo "🔐 管理员账户："
echo "  用户名：admin"
echo "  密码：admin123"
echo ""
echo "🚀 启动服务器："
echo "  python3 manage.py runserver"
echo ""
echo "============================================================"
