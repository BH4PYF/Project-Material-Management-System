#!/usr/bin/env python3
"""
初始化材料分类和清单分类
"""

import os
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'minierp.settings')
django.setup()

from inventory.models import Category, SubcontractList

def init_material_categories():
    """初始化材料分类"""
    print("开始初始化材料分类...")
    
    # 检查是否已有材料分类
    if Category.objects.exists():
        print("材料分类已存在，跳过初始化")
        return
    
    # 初始化材料分类（放入1栏）
    categories = [
        {'code': 'C001', 'name': '钢材'},  # 1栏
        {'code': 'C002', 'name': '水泥'},  # 1栏
        {'code': 'C003', 'name': '砂石'},  # 1栏
        {'code': 'C004', 'name': '木材'},  # 1栏
        {'code': 'C005', 'name': '砖瓦'},  # 1栏
    ]
    
    for cat in categories:
        Category.objects.create(
            code=cat['code'],
            name=cat['name']
        )
        print(f"创建材料分类: {cat['name']}")
    
    print("材料分类初始化完成！")

def init_subcontract_categories():
    """初始化清单分类"""
    print("\n开始初始化清单分类...")
    
    # 检查是否已有清单分类
    if SubcontractList.objects.exists():
        print("清单分类已存在，跳过初始化")
        return
    
    # 初始化清单分类（编号为BOQ0001开始）
    categories = [
        {'code': 'BOQ0001', 'name': '基础工程', 'category': '基础工程', 'unit': '平方米', 'reference_price': 100},
        {'code': 'BOQ0002', 'name': '房屋建筑', 'category': '房屋建筑', 'unit': '平方米', 'reference_price': 2000},
        {'code': 'BOQ0003', 'name': '市政工程', 'category': '市政工程', 'unit': '米', 'reference_price': 500},
        {'code': 'BOQ0004', 'name': '特种加固', 'category': '特种加固', 'unit': '平方米', 'reference_price': 1500},
        {'code': 'BOQ0005', 'name': '装饰装修', 'category': '装饰装修', 'unit': '平方米', 'reference_price': 800},
    ]
    
    for cat in categories:
        SubcontractList.objects.create(
            code=cat['code'],
            name=cat['name'],
            category=cat['category'],
            construction_params='标准施工参数',
            unit=cat['unit'],
            reference_price=cat['reference_price']
        )
        print(f"创建清单分类: {cat['name']} (编号: {cat['code']})")
    
    print("清单分类初始化完成！")

if __name__ == '__main__':
    init_material_categories()
    init_subcontract_categories()
    print("\n所有分类初始化完成！")
