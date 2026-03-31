import pytest
from decimal import Decimal
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse

from ..models import Category, Material, Project, Supplier, InboundRecord, Profile


class MaterialViewsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        from django.contrib.auth.models import Permission
        from django.contrib.contenttypes.models import ContentType
        
        cls.user = User.objects.create_user(username='admin', password='testpass123', is_staff=True)
        cls.profile = Profile.objects.create(user=cls.user, role='admin')
        
        # 添加Django权限
        material_content_type = ContentType.objects.get_for_model(Material)
        material_permissions = Permission.objects.filter(content_type=material_content_type)
        cls.user.user_permissions.add(*material_permissions)
        
        cls.category = Category.objects.create(code='TEST', name='测试分类')
        cls.material = Material.objects.create(
            code='MAT001', name='测试材料', category=cls.category,
            unit='个', standard_price=Decimal('10.00'), safety_stock=10
        )

    def setUp(self):
        self.client = Client()
        self.client.login(username='admin', password='testpass123')

    def test_material_list_view(self):
        response = self.client.get(reverse('material_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '测试材料')
        self.assertContains(response, 'MAT001')

    def test_material_save_create(self):
        data = {
            'name': '新材料',
            'category_id': self.category.id,
            'unit': '个',
            'standard_price': '20.00',
            'safety_stock': '5',
            'spec': '规格1',
            'remark': '测试备注'
        }
        response = self.client.post(reverse('material_save'), data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'success': True, 'message': '保存成功'})
        self.assertTrue(Material.objects.filter(name='新材料').exists())

    def test_material_save_update(self):
        data = {
            'id': self.material.id,
            'name': '更新材料',
            'category_id': self.category.id,
            'unit': '个',
            'standard_price': '15.00',
            'safety_stock': '8',
            'spec': '更新规格',
            'remark': '更新备注'
        }
        response = self.client.post(reverse('material_save'), data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'success': True, 'message': '保存成功'})
        self.material.refresh_from_db()
        self.assertEqual(self.material.name, '更新材料')


class ProjectViewsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        from django.contrib.auth.models import Permission
        from django.contrib.contenttypes.models import ContentType
        
        cls.user = User.objects.create_user(username='admin', password='testpass123', is_staff=True)
        cls.profile = Profile.objects.create(user=cls.user, role='admin')
        
        # 添加Django权限
        project_content_type = ContentType.objects.get_for_model(Project)
        project_permissions = Permission.objects.filter(content_type=project_content_type)
        cls.user.user_permissions.add(*project_permissions)
        
        cls.project = Project.objects.create(
            code='PRJ001', name='测试项目', manager='张三',
            location='测试地点', budget=Decimal('1000000.00')
        )

    def setUp(self):
        self.client = Client()
        self.client.login(username='admin', password='testpass123')

    def test_project_list_view(self):
        response = self.client.get(reverse('project_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '测试项目')
        self.assertContains(response, 'PRJ001')

    def test_project_save_create(self):
        data = {
            'name': '新项目',
            'manager': '李四',
            'location': '新地点',
            'budget': '500000.00',
            'status': 'active',
            'remark': '测试项目'
        }
        response = self.client.post(reverse('project_save'), data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'success': True, 'message': '保存成功'})
        self.assertTrue(Project.objects.filter(name='新项目').exists())


class SupplierViewsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        from django.contrib.auth.models import Permission
        from django.contrib.contenttypes.models import ContentType
        
        cls.user = User.objects.create_user(username='admin', password='testpass123', is_staff=True)
        cls.profile = Profile.objects.create(user=cls.user, role='admin')
        
        # 添加Django权限
        supplier_content_type = ContentType.objects.get_for_model(Supplier)
        supplier_permissions = Permission.objects.filter(content_type=supplier_content_type)
        cls.user.user_permissions.add(*supplier_permissions)
        
        cls.category = Category.objects.create(code='TEST', name='测试分类')
        cls.supplier = Supplier.objects.create(
            code='SUP001', name='测试供应商', contact='王五',
            phone='13800138000', address='测试地址', main_type=cls.category
        )

    def setUp(self):
        self.client = Client()
        self.client.login(username='admin', password='testpass123')

    def test_supplier_list_view(self):
        response = self.client.get(reverse('supplier_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '测试供应商')
        self.assertContains(response, 'SUP001')

    def test_supplier_save_create(self):
        data = {
            'name': '新供应商',
            'contact': '赵六',
            'phone': '13900139000',
            'address': '新地址',
            'main_type': self.category.id,
            'credit_rating': 'good',
            'remark': '测试供应商'
        }
        response = self.client.post(reverse('supplier_save'), data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Supplier.objects.filter(name='新供应商').exists())


class InboundViewsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='admin', password='testpass123', is_staff=True)
        cls.profile = Profile.objects.create(user=cls.user, role='admin')
        cls.category = Category.objects.create(code='TEST', name='测试分类')
        cls.material = Material.objects.create(
            code='MAT001', name='测试材料', category=cls.category,
            unit='个', standard_price=Decimal('10.00')
        )
        cls.project = Project.objects.create(code='PRJ001', name='测试项目', location='测试地点')
        cls.supplier = Supplier.objects.create(code='SUP001', name='测试供应商')

    def setUp(self):
        self.client = Client()
        self.client.login(username='admin', password='testpass123')

    def test_inbound_list_view(self):
        response = self.client.get(reverse('inbound_list'))
        self.assertEqual(response.status_code, 200)

    def test_inbound_save(self):
        data = {
            'project_id': self.project.id,
            'material_id': self.material.id,
            'supplier_id': self.supplier.id,
            'date': '2026-03-27',
            'quantity': '10',
            'unit_price': '15.00',
            'batch_no': 'BATCH001',
            'spec': '测试规格',
            'remark': '测试入库'
        }
        response = self.client.post(reverse('inbound_save'), data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'success': True, 'message': '保存成功'})
        self.assertTrue(InboundRecord.objects.exists())

    def test_inbound_detail_api(self):
        inbound = InboundRecord.objects.create(
            no='IN20260327001', project=self.project, material=self.material,
            supplier=self.supplier, date='2026-03-27', quantity=Decimal('5'),
            unit_price=Decimal('12.00'), total_amount=Decimal('60.00'),
            operator=self.user, location='测试地点', spec='测试规格'
        )
        response = self.client.get(reverse('inbound_detail_api', kwargs={'pk': inbound.id}))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['no'], 'IN20260327001')
        self.assertEqual(data['quantity'], '5.00')


class DashboardViewsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='admin', password='testpass123', is_staff=True)
        cls.profile = Profile.objects.create(user=cls.user, role='admin')

    def setUp(self):
        self.client = Client()
        self.client.login(username='admin', password='testpass123')

    def test_dashboard_view(self):
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '材料管理系统')


class ReportViewsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='admin', password='testpass123', is_staff=True)
        cls.profile = Profile.objects.create(user=cls.user, role='admin')
        cls.category = Category.objects.create(code='TEST', name='测试分类')
        cls.material = Material.objects.create(
            code='MAT001', name='测试材料', category=cls.category,
            unit='个', standard_price=Decimal('10.00')
        )
        cls.project = Project.objects.create(code='PRJ001', name='测试项目', location='测试地点')
        cls.supplier = Supplier.objects.create(code='SUP001', name='测试供应商')
        cls.inbound = InboundRecord.objects.create(
            no='IN20260327001', project=cls.project, material=cls.material,
            supplier=cls.supplier, date='2026-03-27', quantity=Decimal('10'),
            unit_price=Decimal('15.00'), total_amount=Decimal('150.00'),
            operator=cls.user, location='测试地点', spec='测试规格'
        )

    def setUp(self):
        self.client = Client()
        self.client.login(username='admin', password='testpass123')

    def test_report_page_view(self):
        response = self.client.get(reverse('report_page'))
        self.assertEqual(response.status_code, 200)

    def test_chart_data_api(self):
        response = self.client.get(reverse('chart_data_api'), {'type': 'stock'})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('data', data)
