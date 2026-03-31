#!/usr/bin/env python3
"""
删除测试数据脚本
"""
import os
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'material_system.settings')
django.setup()

from inventory.models import Project, Material, Supplier, InboundRecord, PurchasePlan, Delivery

def delete_test_data():
    """删除测试数据"""
    print("开始删除测试数据...")
    
    # 先删除软删除的发货单
    soft_deleted_deliveries = Delivery.all_objects.filter(is_deleted=True)
    print(f"发现 {soft_deleted_deliveries.count()} 个软删除的发货单，准备硬删除")
    for delivery in soft_deleted_deliveries:
        print(f"硬删除发货单: {delivery.no}")
        delivery.hard_delete()
    print("软删除的发货单已硬删除")
    
    # 再删除软删除的采购计划（这些可能引用了测试材料）
    soft_deleted_plans = PurchasePlan.all_objects.filter(is_deleted=True)
    print(f"发现 {soft_deleted_plans.count()} 个软删除的采购计划，准备硬删除")
    for plan in soft_deleted_plans:
        print(f"硬删除采购计划: {plan.no}")
        plan.hard_delete()
    print("软删除的采购计划已硬删除")
    
    # 删除测试材料
    test_material = Material.objects.filter(code='TEST-MAT').first()
    if test_material:
        print(f"删除测试材料: {test_material.name}")
        test_material.delete()
        print("测试材料删除成功")
    else:
        print("测试材料不存在")
    
    # 删除测试项目
    test_project = Project.objects.filter(code='TEST-PROJ').first()
    if test_project:
        # 检查是否有采购计划
        if PurchasePlan.objects.filter(project=test_project).exists():
            print("测试项目有采购计划，无法删除")
        # 检查是否有入库记录
        elif InboundRecord.objects.filter(project=test_project).exists():
            print("测试项目有入库记录，无法删除")
        else:
            print(f"删除测试项目: {test_project.name}")
            test_project.delete()
            print("测试项目删除成功")
    else:
        print("测试项目不存在")
    
    # 查看删除后的数据
    print("\n删除后的数据统计:")
    print(f"项目: {Project.objects.count()}")
    print(f"材料: {Material.objects.count()}")
    print(f"供应商: {Supplier.objects.count()}")
    print(f"入库记录: {InboundRecord.objects.count()}")
    print(f"采购计划: {PurchasePlan.objects.count()}")
    print(f"发货单: {Delivery.objects.count()}")

if __name__ == "__main__":
    delete_test_data()
