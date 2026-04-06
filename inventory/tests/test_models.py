import pytest
from decimal import Decimal
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from ..models import (
    Category, Material, Supplier,
    Project, InboundRecord, PurchasePlan,
    SystemSetting,
)


class CategoryModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(
            name="测试分类",
            code="TEST001",
            remark="测试用分类"
        )

    def test_category_creation(self):
        self.assertEqual(self.category.name, "测试分类")
        self.assertEqual(self.category.code, "TEST001")
        self.assertEqual(str(self.category), "测试分类")

    def test_category_unique_code(self):
        with pytest.raises(Exception):
            Category.objects.create(name="另一个分类", code="TEST001")


class MaterialModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(name="钢材", code="STEEL")
        cls.material = Material.objects.create(
            name="螺纹钢",
            code="HRB400",
            category=cls.category,
            unit="吨",
            standard_price=Decimal('3800.00'),
            spec="Φ25",
            safety_stock=10
        )

    def test_material_creation(self):
        self.assertEqual(self.material.name, "螺纹钢")
        self.assertEqual(self.material.category, self.category)
        self.assertEqual(self.material.unit, "吨")

    def test_material_str(self):
        self.assertEqual(str(self.material), "HRB400 - 螺纹钢 (Φ25)")

    def test_get_total_inbound(self):
        stock = self.material.get_total_inbound()
        self.assertEqual(stock, Decimal('0'))


class SupplierModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(name="钢材", code="STEEL")
        cls.supplier = Supplier.objects.create(
            name="测试供应商",
            code="SUP001",
            contact="张三",
            phone="13800138000",
            address="北京市朝阳区",
            main_type=cls.category
        )

    def test_supplier_creation(self):
        self.assertEqual(self.supplier.name, "测试供应商")
        self.assertEqual(self.supplier.contact, "张三")
        self.assertEqual(str(self.supplier), "SUP001 - 测试供应商")


class ProjectModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.project = Project.objects.create(
            name="测试项目",
            code="P001",
            manager="李四",
            budget=Decimal('1000000.00')
        )

    def test_project_creation(self):
        self.assertEqual(self.project.name, "测试项目")
        self.assertEqual(self.project.code, "P001")
        self.assertEqual(str(self.project), "P001 - 测试项目")

    def test_soft_delete(self):
        self.assertFalse(self.project.is_deleted)
        self.assertIsNone(self.project.deleted_at)
        self.project.delete()
        self.project.refresh_from_db()
        self.assertTrue(self.project.is_deleted)
        self.assertIsNotNone(self.project.deleted_at)
        self.assertFalse(Project.objects.filter(pk=self.project.pk).exists())
        self.assertTrue(Project.all_objects.filter(pk=self.project.pk).exists())


class InboundRecordModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='operator', password='pass12345')
        cls.category = Category.objects.create(name="测试分类", code="TEST")
        cls.supplier = Supplier.objects.create(
            name="测试供应商", code="SUP001", contact="张三", phone="13800138000"
        )
        cls.material = Material.objects.create(
            name="测试材料", code="MT001", category=cls.category,
            unit="个", standard_price=Decimal('10.00'), safety_stock=5
        )
        cls.project = Project.objects.create(name="测试项目", code="P001")

    def test_save_calculates_total(self):
        record = InboundRecord.objects.create(
            no="IN20260322001", material=self.material,
            quantity=Decimal('10'), unit_price=Decimal('9.50'),
            supplier=self.supplier, project=self.project,
            operator=self.user, date='2026-03-22',
            spec='规格1',
        )
        self.assertEqual(record.total_amount, Decimal('95.00'))

    def test_inbound_increases_total(self):
        initial = self.material.get_total_inbound()
        InboundRecord.objects.create(
            no="IN20260322001", material=self.material,
            quantity=Decimal('10'), unit_price=Decimal('9.50'),
            supplier=self.supplier, project=self.project,
            operator=self.user, date='2026-03-22',
            spec='规格1',
        )
        new_total = self.material.get_total_inbound()
        self.assertEqual(new_total, initial + 10)

    def test_soft_delete(self):
        record = InboundRecord.objects.create(
            no="IN20260322002", material=self.material,
            quantity=Decimal('5'), unit_price=Decimal('10'),
            supplier=self.supplier, project=self.project,
            operator=self.user, date='2026-03-22',
            spec='规格1',
        )
        self.assertFalse(record.is_deleted)
        record.delete()
        record.refresh_from_db()
        self.assertTrue(record.is_deleted)
        self.assertIsNotNone(record.deleted_at)
        self.assertFalse(InboundRecord.objects.filter(pk=record.pk).exists())
        self.assertTrue(InboundRecord.all_objects.filter(pk=record.pk).exists())

    def test_validate_negative_quantity(self):
        record = InboundRecord(
            no="IN_NEG", material=self.material,
            quantity=Decimal('-5'), unit_price=Decimal('10'),
            supplier=self.supplier, project=self.project,
            operator=self.user, date='2026-03-22',
            spec='规格1',
        )
        with self.assertRaises(ValidationError):
            record.clean()

    def test_validate_negative_price(self):
        record = InboundRecord(
            no="IN_NEGP", material=self.material,
            quantity=Decimal('5'), unit_price=Decimal('-1'),
            supplier=self.supplier, project=self.project,
            operator=self.user, date='2026-03-22',
            spec='规格1',
        )
        with self.assertRaises(ValidationError):
            record.clean()


class PurchasePlanModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='planner', password='pass12345')
        cls.category = Category.objects.create(name="钢材", code="STEEL")
        cls.material = Material.objects.create(
            name="螺纹钢", code="HRB400", category=cls.category, unit="吨"
        )
        cls.project = Project.objects.create(name="测试项目", code="P001")

    def test_save_calculates_total(self):
        plan = PurchasePlan.objects.create(
            no="PP20260322001", project=self.project,
            material=self.material, quantity=Decimal('100'),
            unit_price=Decimal('3800'), operator=self.user,
        )
        self.assertEqual(plan.total_amount, Decimal('380000'))


class SystemSettingTest(TestCase):
    def test_get_default(self):
        val = SystemSetting.get_setting('nonexistent', 'default_val')
        self.assertEqual(val, 'default_val')

    def test_set_and_get(self):
        SystemSetting.set_setting('test_key', 'test_value', '测试用')
        val = SystemSetting.get_setting('test_key')
        self.assertEqual(val, 'test_value')

    def test_update_existing(self):
        SystemSetting.set_setting('key1', 'v1')
        SystemSetting.set_setting('key1', 'v2')
        self.assertEqual(SystemSetting.get_setting('key1'), 'v2')
