from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0024_alter_purchaseplan_status'),
    ]

    operations = [
        # 为材料添加名称和规格的索引（用于搜索）
        migrations.AddIndex(
            model_name='material',
            index=models.Index(fields=['name'], name='inventory_material_name_idx'),
        ),
        migrations.AddIndex(
            model_name='material',
            index=models.Index(fields=['spec'], name='inventory_material_spec_idx'),
        ),
        
        # 为入库记录添加材料和项目的组合索引（用于统计查询）
        migrations.AddIndex(
            model_name='inboundrecord',
            index=models.Index(fields=['material', 'project'], name='inventory_inboundrecord_material_project_idx'),
        ),
        
        # 为项目添加状态索引（用于状态筛选）
        migrations.AddIndex(
            model_name='project',
            index=models.Index(fields=['status'], name='inventory_project_status_idx'),
        ),
        
        # 为采购计划添加状态索引（用于状态筛选）
        migrations.AddIndex(
            model_name='purchaseplan',
            index=models.Index(fields=['status'], name='inventory_purchaseplan_status_idx'),
        ),
        
        # 为发货单添加状态索引（用于状态筛选）
        migrations.AddIndex(
            model_name='delivery',
            index=models.Index(fields=['status'], name='inventory_delivery_status_idx'),
        ),
        
        # 为供应商添加名称索引（用于搜索）
        migrations.AddIndex(
            model_name='supplier',
            index=models.Index(fields=['name'], name='inventory_supplier_name_idx'),
        ),
    ]
