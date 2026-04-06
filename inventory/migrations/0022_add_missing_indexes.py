from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0021_add_spec_to_purchaseplan'),
    ]

    operations = [
        # 为采购计划添加项目和材料的组合索引
        migrations.AddIndex(
            model_name='purchaseplan',
            index=models.Index(fields=['project', 'material'], name='inventory_purchaseplan_project_material_idx'),
        ),
        # 为入库记录添加项目索引
        migrations.AddIndex(
            model_name='inboundrecord',
            index=models.Index(fields=['project'], name='inventory_inboundrecord_project_idx'),
        ),
        # 为入库记录添加材料索引
        migrations.AddIndex(
            model_name='inboundrecord',
            index=models.Index(fields=['material'], name='inventory_inboundrecord_material_idx'),
        ),
        # 为发货单添加采购计划索引
        migrations.AddIndex(
            model_name='delivery',
            index=models.Index(fields=['purchase_plan'], name='inventory_delivery_purchase_plan_idx'),
        ),
        # 为发货单添加供应商索引
        migrations.AddIndex(
            model_name='delivery',
            index=models.Index(fields=['supplier'], name='inventory_delivery_supplier_idx'),
        ),
        # 为材料添加分类索引
        migrations.AddIndex(
            model_name='material',
            index=models.Index(fields=['category'], name='inventory_material_category_idx'),
        ),
        # 为供应商添加主营类型索引
        migrations.AddIndex(
            model_name='supplier',
            index=models.Index(fields=['main_type'], name='inventory_supplier_main_type_idx'),
        ),
    ]
