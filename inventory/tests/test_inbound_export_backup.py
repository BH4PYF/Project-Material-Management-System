import json
import pytest
from decimal import Decimal
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.exceptions import ValidationError

from ..models import (
    Profile, Category, Material, Supplier,
    Project, InboundRecord, PurchasePlan, Delivery,
)


class ViewTestBase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='testuser', password='testpass123', first_name='测试'
        )
        cls.profile = Profile.objects.create(user=cls.user, role='admin', phone='12345678')

    def login(self):
        self.client.login(username='testuser', password='testpass123')


class InboundFlowTest(ViewTestBase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.category = Category.objects.create(name="钢材", code="STEEL")
        cls.material = Material.objects.create(
            name="测试材料", code="MT001", category=cls.category, unit="吨"
        )
        cls.supplier = Supplier.objects.create(
            name="测试供应商", code="SUP001", contact="张三", phone="13800138000"
        )
        cls.project = Project.objects.create(name="测试项目", code="P001")

    def test_inbound_create_flow(self):
        self.login()
        response = self.client.post(reverse('inbound_save'), {
            'project_id': self.project.pk,
            'material_id': self.material.pk,
            'date': '2026-03-22',
            'quantity': '100',
            'unit_price': '3800',
            'supplier_id': self.supplier.pk,
            'spec': 'Φ25',
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(InboundRecord.objects.count(), 1)
        record = InboundRecord.objects.first()
        self.assertEqual(record.total_amount, Decimal('380000'))

    def test_inbound_delete_flow(self):
        self.login()
        record = InboundRecord.objects.create(
            no="IN_DEL", material=self.material,
            quantity=Decimal('10'), unit_price=Decimal('100'),
            supplier=self.supplier, project=self.project,
            operator=self.user, date='2026-03-22',
            spec='规格1',
        )
        response = self.client.post(reverse('inbound_delete', args=[record.pk]))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])

    def test_inbound_list_pagination(self):
        self.login()
        for i in range(25):
            InboundRecord.objects.create(
                no=f"IN_PAGE_{i:03d}", material=self.material,
                quantity=Decimal('1'), unit_price=Decimal('10'),
                supplier=self.supplier, project=self.project,
                operator=self.user, date='2026-03-22',
                spec='规格1',
            )
        response = self.client.get(reverse('inbound_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['page_obj'].has_next())


class ExportTest(ViewTestBase):
    def test_export_inbound_excel(self):
        self.login()
        response = self.client.get(reverse('export_excel'), {'type': 'inbound'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response['Content-Type'],
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

    def test_export_inventory_excel(self):
        self.login()
        response = self.client.get(reverse('export_excel'), {'type': 'inventory'})
        self.assertEqual(response.status_code, 200)


class BackupRestoreTest(ViewTestBase):
    def test_backup_data(self):
        self.login()
        response = self.client.post(reverse('backup_data'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        data = json.loads(response.content)
        self.assertIn('timestamp', data)
        self.assertIn('projects', data)

    def test_restore_data(self):
        self.login()
        Category.objects.create(name="原分类", code="CAT_ORIG")
        backup_data = json.dumps({
            'timestamp': '2026-03-22T00:00:00',
            'categories': [{'code': 'CAT_NEW', 'name': '新分类', 'remark': ''}],
        })
        from django.core.files.uploadedfile import SimpleUploadedFile
        f = SimpleUploadedFile("backup.json", backup_data.encode('utf-8'), content_type='application/json')
        response = self.client.post(reverse('restore_data'), {'file': f})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertTrue(Category.objects.filter(code='CAT_NEW').exists())


class RestoreEdgeCaseTest(ViewTestBase):
    def test_restore_invalid_json(self):
        self.login()
        from django.core.files.uploadedfile import SimpleUploadedFile
        f = SimpleUploadedFile("bad.json", b"not a json!", content_type='application/json')
        response = self.client.post(reverse('restore_data'), {'file': f})
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json())

    def test_restore_empty_data(self):
        self.login()
        from django.core.files.uploadedfile import SimpleUploadedFile
        f = SimpleUploadedFile("empty.json", b'{}', content_type='application/json')
        response = self.client.post(reverse('restore_data'), {'file': f})
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json())

    def test_restore_no_file(self):
        self.login()
        response = self.client.post(reverse('restore_data'))
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json())

    def test_restore_unknown_keys_ignored(self):
        self.login()
        from django.core.files.uploadedfile import SimpleUploadedFile
        backup = json.dumps({
            'timestamp': '2026-03-22T00:00:00',
            'unknown_table': [{'foo': 'bar'}],
        })
        f = SimpleUploadedFile("unknown.json", backup.encode('utf-8'), content_type='application/json')
        response = self.client.post(reverse('restore_data'), {'file': f})
        self.assertEqual(response.status_code, 200)

    def test_restore_with_extra_fields_filtered(self):
        self.login()
        Category.objects.create(name="原分类", code="CAT_SEC")
        from django.core.files.uploadedfile import SimpleUploadedFile
        backup = json.dumps({
            'timestamp': '2026-03-22T00:00:00',
            'categories': [{'code': 'CAT_SEC', 'name': '修改后的分类', 'remark': '', 'id': 99999}],
        })
        f = SimpleUploadedFile("fields.json", backup.encode('utf-8'), content_type='application/json')
        response = self.client.post(reverse('restore_data'), {'file': f})
        self.assertEqual(response.status_code, 200)
        cat = Category.objects.get(code='CAT_SEC')
        self.assertNotEqual(cat.pk, 99999)
        self.assertEqual(cat.name, '修改后的分类')


@pytest.mark.slow
class ConcurrencySafetyTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="并发测试", code="CONC")
        self.material = Material.objects.create(
            name="并发材料", code="MT_C01", category=self.category, unit="吨", spec="Φ25",
        )
        self.supplier = Supplier.objects.create(
            name="并发供应商", code="SUP_C01", contact="测试", phone="13500135000",
        )
        self.project = Project.objects.create(name="并发项目", code="P_C01")
        self.user = User.objects.create_user(username='conc_user', password='pass12345')
        Profile.objects.create(user=self.user, role='management')

    def test_concurrent_quick_receive_idempotent(self):
        plan = PurchasePlan.objects.create(
            no="PP_C001", project=self.project, material=self.material,
            quantity=Decimal('100'), unit_price=Decimal('50'),
            status=PurchasePlan.STATUS_SHIPPED, operator=self.user,
        )
        delivery = Delivery.objects.create(
            no='DL_C001', purchase_plan=plan,
            actual_quantity=Decimal('100'), actual_unit_price=Decimal('50'),
            shipping_method='special', supplier=self.supplier,
            status=Delivery.STATUS_SHIPPED,
        )

        client = Client()
        client.login(username='conc_user', password='pass12345')

        response = client.post(reverse('quick_receive_confirm'), {
            'delivery_id': delivery.pk,
            'receive_date': '2026-03-24',
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])

        response = client.post(reverse('quick_receive_confirm'), {
            'delivery_id': delivery.pk,
            'receive_date': '2026-03-24',
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn('已收货', response.json()['error'])

        self.assertEqual(InboundRecord.objects.count(), 1)

    def test_inbound_negative_quantity_rejected_via_save(self):
        record = InboundRecord(
            no="IN_NEG_SAVE", material=self.material,
            quantity=Decimal('-5'), unit_price=Decimal('10'),
            supplier=self.supplier, project=self.project,
            operator=self.user, date='2026-03-24',
            spec='规格1',
        )
        with self.assertRaises(ValidationError):
            record.save()
