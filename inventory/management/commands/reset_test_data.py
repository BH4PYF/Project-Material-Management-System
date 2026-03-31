"""
清除所有数据并生成测试数据
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from inventory.models import Profile, Project, Category, Material, Supplier, InboundRecord, Delivery, PurchasePlan
from django.utils import timezone
from datetime import timedelta
import random


class Command(BaseCommand):
    help = '清除所有数据并生成测试数据'

    def handle(self, *args, **options):
        self.stdout.write('=' * 60)
        self.stdout.write('🗑️  开始清除现有数据...')
        self.stdout.write('=' * 60)

        # 1. 删除所有数据（按依赖顺序，从最底层开始）
        # 先删除依赖其他表的记录
        InboundRecord.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('✓ 已删除所有入库记录'))

        Delivery.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('✓ 已删除所有发货记录'))

        PurchasePlan.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('✓ 已删除所有采购计划'))

        # 再删除基础数据
        Material.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('✓ 已删除所有材料'))

        Supplier.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('✓ 已删除所有供应商'))

        Project.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('✓ 已删除所有项目'))

        Category.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('✓ 已删除所有材料分类'))

        # 保留 admin 用户，删除其他用户
        admin = User.objects.filter(username='admin').first()
        User.objects.exclude(username='admin').delete()
        self.stdout.write(self.style.SUCCESS('✓ 已删除除 admin 外的所有用户'))

        self.stdout.write('\n' + '=' * 60)
        self.stdout.write('✨ 开始生成测试数据...')
        self.stdout.write('=' * 60)

        # 2. 生成基础数据
        categories_data = [
            ('CAT001', '钢材', '建筑用钢材'),
            ('CAT002', '水泥', '普通硅酸盐水泥'),
            ('CAT003', '混凝土', '商品混凝土'),
        ]

        categories = []
        for code, name, remark in categories_data:
            cat, _ = Category.objects.get_or_create(code=code, defaults={'name': name, 'remark': remark})
            categories.append(cat)
        self.stdout.write(f'✓ 已创建 {len(categories)} 个材料分类')

        # 3. 生成项目 (4 个)
        projects_data = [
            ('PRJ001', '科技创新园一期工程', '张工程师', '北京市朝阳区', '2024-01-01', '2025-12-31', 50000000, 'active'),
            ('PRJ002', '地铁 5 号线站点建设', '李工程师', '北京市海淀区', '2024-03-01', '2026-02-28', 80000000, 'active'),
            ('PRJ003', '商业中心综合体', '王工程师', '上海市浦东新区', '2024-06-01', '2026-05-31', 120000000, 'active'),
            ('PRJ004', '住宅小区二期', '赵工程师', '广州市天河区', '2024-09-01', '2026-08-31', 60000000, 'planning'),
        ]

        projects = []
        for code, name, manager, location, start, end, budget, status in projects_data:
            project, _ = Project.objects.get_or_create(
                code=code,
                defaults={
                    'name': name,
                    'manager': manager,
                    'location': location,
                    'start_date': start,
                    'end_date': end,
                    'budget': budget,
                    'status': status,
                }
            )
            projects.append(project)
        self.stdout.write(f'✓ 已创建 {len(projects)} 个项目')

        # 4. 生成供应商 (4 个)
        suppliers_data = [
            ('SUP001', '华东钢铁有限公司', '陈经理', '13800138001', '上海市宝山区', 'AAA', '2020-01-01'),
            ('SUP002', '北方水泥集团', '刘经理', '13800138002', '河北省唐山市', 'AA', '2019-06-01'),
            ('SUP003', '华南建材供应公司', '黄经理', '13800138003', '广东省深圳市', 'AAA', '2021-03-01'),
            ('SUP004', '西南混凝土厂', '周经理', '13800138004', '四川省成都市', 'A', '2022-01-01'),
        ]

        suppliers = []
        for code, name, contact, phone, address, credit, date in suppliers_data:
            supplier, _ = Supplier.objects.get_or_create(
                code=code,
                defaults={
                    'name': name,
                    'contact': contact,
                    'phone': phone,
                    'address': address,
                    'credit_rating': credit,
                    'start_date': date,
                }
            )
            suppliers.append(supplier)
        self.stdout.write(f'✓ 已创建 {len(suppliers)} 个供应商')

        # 5. 生成材料 (每个分类 2-3 个)
        materials_data = [
            # 钢材
            ('MAT001', '螺纹钢 HRB400', 'CAT001', 'Φ12mm', '吨', 4200.00, 100),
            ('MAT002', '盘螺 HRB400', 'CAT001', 'Φ8mm', '吨', 4350.00, 80),
            ('MAT003', '线材 HPB300', 'CAT001', 'Φ6.5mm', '吨', 4100.00, 60),
            # 水泥
            ('MAT004', '普通硅酸盐水泥 P.O 42.5', 'CAT002', '袋装 50kg', '吨', 450.00, 200),
            ('MAT005', '复合硅酸盐水泥 P.C 32.5', 'CAT002', '袋装 50kg', '吨', 380.00, 150),
            # 混凝土
            ('MAT006', 'C30 商品混凝土', 'CAT003', '立方米', '立方米', 420.00, 500),
            ('MAT007', 'C35 商品混凝土', 'CAT003', '立方米', '立方米', 450.00, 400),
        ]

        materials = []
        for code, name, cat_code, spec, unit, price, stock in materials_data:
            material, _ = Material.objects.get_or_create(
                code=code,
                defaults={
                    'name': name,
                    'category_id': cat_code,
                    'spec': spec,
                    'unit': unit,
                    'standard_price': price,
                    'safety_stock': stock,
                }
            )
            materials.append(material)
        self.stdout.write(f'✓ 已创建 {len(materials)} 个材料')

        # 6. 生成入库记录 (每个项目 2-3 条)
        admin_user = admin if admin else User.objects.filter(is_superuser=True).first()
        if not admin_user:
            admin_user = User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
            Profile.objects.get_or_create(user=admin_user, defaults={'role': 'admin'})

        inbound_count = 0
        for project in projects[:3]:  # 前 3 个项目
            num_records = random.randint(2, 3)
            for i in range(num_records):
                material = random.choice(materials)
                supplier = random.choice(suppliers)

                quantity = random.uniform(10, 100)
                price = material.standard_price * random.uniform(0.95, 1.05)

                inbound_date = timezone.now().date() - timedelta(days=random.randint(1, 30))

                InboundRecord.objects.create(
                    project=project,
                    material=material,
                    supplier=supplier,
                    quantity=quantity,
                    unit_price=price,
                    total_amount=quantity * price,
                    inbound_date=inbound_date,
                    operator=admin_user,
                    location=project.location,
                    spec=material.spec,
                )
                inbound_count += 1

        self.stdout.write(f'✓ 已创建 {inbound_count} 条入库记录')

        # 7. 生成发货记录 (3 条)
        delivery_count = 0
        for i in range(3):
            project = random.choice(projects[:3])

            # 使用采购计划编号
            delivery_no = plan.no
            delivery_date = timezone.now().date() - timedelta(days=random.randint(1, 15))

            Delivery.objects.create(
                no=delivery_no,
                project=project,
                delivery_date=delivery_date,
                status='shipped' if random.random() > 0.5 else 'pending',
                remark=f'测试发货记录 {i+1}',
            )
            delivery_count += 1

        self.stdout.write(f'✓ 已创建 {delivery_count} 条发货记录')

        self.stdout.write('\n' + '=' * 60)
        self.stdout.write(self.style.SUCCESS('✅ 测试数据生成完成！'))
        self.stdout.write('=' * 60)

        # 显示统计
        self.stdout.write('\n📊 数据统计：')
        self.stdout.write(f'  - 材料分类：{Category.objects.count()} 个')
        self.stdout.write(f'  - 项目：{Project.objects.count()} 个')
        self.stdout.write(f'  - 供应商：{Supplier.objects.count()} 个')
        self.stdout.write(f'  - 材料：{Material.objects.count()} 个')
        self.stdout.write(f'  - 入库记录：{InboundRecord.objects.count()} 条')
        self.stdout.write(f'  - 发货记录：{Delivery.objects.count()} 条')
        self.stdout.write(f'  - 用户：{User.objects.count()} 个')

        self.stdout.write('\n🔐 管理员账户：')
        self.stdout.write('  用户名：admin')
        self.stdout.write('  密码：admin123')
