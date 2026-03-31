from decimal import Decimal
from typing import List, Dict, Optional, Tuple
from django.db.models import Q, Sum
from django.db import transaction

from inventory.models import Material, Category, InboundRecord, PurchasePlan


class MaterialService:
    """材料管理服务"""
    
    @staticmethod
    def get_materials_with_statistics(project_id: Optional[int] = None, 
                                   category_id: Optional[int] = None,
                                   search_query: Optional[str] = None) -> List[Dict]:
        """获取材料列表并包含统计信息"""
        materials_qs = Material.objects.select_related('category').all()
        
        # 应用筛选条件
        if category_id:
            materials_qs = materials_qs.filter(category_id=category_id)
        if search_query:
            materials_qs = materials_qs.filter(
                Q(code__icontains=search_query) | 
                Q(name__icontains=search_query) | 
                Q(spec__icontains=search_query)
            )
        
        # 使用子查询让数据库做 ID 筛选，避免将全部材料对象加载到 Python 内存
        inbound_agg = InboundRecord.objects.filter(
            material_id__in=materials_qs.values('pk')
        ).values('material_id').annotate(
            total_qty=Sum('quantity'),
            total_amount=Sum('total_amount'),
        )
        
        # 创建聚合映射
        agg_map = {
            row['material_id']: {
                'total_qty': row['total_qty'] or Decimal('0'),
                'total_amount': row['total_amount'] or Decimal('0'),
            }
            for row in inbound_agg
        }
        
        # 构建返回数据
        material_data = []
        for material in materials_qs:
            agg = agg_map.get(material.pk, {'total_qty': Decimal('0'), 'total_amount': Decimal('0')})
            inbound_qty = agg['total_qty']
            inbound_amount = agg['total_amount']
            avg_cost = (inbound_amount / inbound_qty) if inbound_qty > 0 else Decimal('0')
            
            # 入库量状态判断
            if inbound_qty <= 0:
                status_key, status_label = 'danger', '无入库'
            elif inbound_qty <= material.safety_stock * Decimal('0.5'):
                status_key, status_label = 'warning', '严重不足'
            elif inbound_qty <= material.safety_stock:
                status_key, status_label = 'caution', '入库不足'
            else:
                status_key, status_label = 'normal', '正常'
            
            material_data.append({
                'obj': material,
                'stock': inbound_qty,
                'status_key': status_key,
                'status_label': status_label,
                'avg_cost': avg_cost,
                'stock_value': inbound_qty * avg_cost if inbound_qty > 0 else Decimal('0'),
            })
        
        return material_data
    
    @staticmethod
    def create_material(data: Dict) -> Tuple[Material, Optional[str]]:
        """创建材料"""
        from inventory.views.utils import generate_code
        
        try:
            with transaction.atomic():
                # 检查重复
                existing = Material.objects.filter(
                    name=data['name'],
                    spec=data.get('spec', '')
                ).first()
                
                if existing:
                    return None, f'材料已存在：{existing.name}（规格：{existing.spec or "无"}, ' \
                               f'分类：{existing.category.name}, 单位：{existing.unit}, ' \
                               f'编号：{existing.code}），请勿重复创建'
                
                material = Material()
                material.code = generate_code('MAT', Material)
                material.name = data['name']
                material.category_id = data['category_id']
                material.spec = data.get('spec', '')
                material.unit = data['unit']
                material.standard_price = data.get('standard_price', Decimal('0'))
                material.safety_stock = data.get('safety_stock', Decimal('0'))
                material.remark = data.get('remark', '')
                material.save()
                
                return material, None
        except Exception as e:
            return None, str(e)
    
    @staticmethod
    def update_material(material_id: int, data: Dict) -> Tuple[Material, Optional[str]]:
        """更新材料"""
        try:
            with transaction.atomic():
                material = Material.objects.get(pk=material_id)
                
                # 检查重复（排除自身）
                duplicate = Material.objects.filter(
                    name=data['name'],
                    spec=data.get('spec', '')
                ).exclude(pk=material_id).first()
                
                if duplicate:
                    return None, f'材料已存在：{duplicate.name}（规格：{duplicate.spec or "无"}, ' \
                               f'分类：{duplicate.category.name}, 单位：{duplicate.unit}, ' \
                               f'编号：{duplicate.code}），请使用其他参数'
                
                material.name = data['name']
                material.category_id = data['category_id']
                material.spec = data.get('spec', '')
                material.unit = data['unit']
                material.standard_price = data.get('standard_price', Decimal('0'))
                material.safety_stock = data.get('safety_stock', Decimal('0'))
                material.remark = data.get('remark', '')
                material.save()
                
                return material, None
        except Material.DoesNotExist:
            return None, '材料不存在'
        except Exception as e:
            return None, str(e)
    
    @staticmethod
    def delete_material(material_id: int) -> Tuple[bool, Optional[str]]:
        """删除材料"""
        try:
            material = Material.objects.get(pk=material_id)
            
            # 检查是否有入库记录
            if material.inbound_records.exists():
                return False, '该材料已有入库记录，无法删除'
            
            # 检查是否有采购计划
            if material.purchase_plans.exists():
                return False, '该材料已有采购计划，无法删除'
            
            material.delete()
            return True, None
        except Material.DoesNotExist:
            return False, '材料不存在'
        except Exception as e:
            # 捕获外键保护异常
            if 'protected foreign keys' in str(e):
                if 'PurchasePlan.material' in str(e):
                    return False, '该材料已有采购计划，无法删除'
                elif 'InboundRecord.material' in str(e):
                    return False, '该材料已有入库记录，无法删除'
                else:
                    return False, '该材料被其他记录引用，无法删除'
            return False, str(e)
    
    @staticmethod
    def check_material_duplicate(name: str, spec: str, exclude_id: Optional[int] = None) -> Tuple[bool, Optional[Dict]]:
        """检查材料是否重复"""
        if not name:
            return False, None
        
        query = Material.objects.filter(name=name, spec=spec)
        if exclude_id:
            query = query.exclude(pk=exclude_id)
        
        duplicate = query.select_related('category').first()
        
        if duplicate:
            return True, {
                'code': duplicate.code,
                'message': f'{duplicate.name}（规格：{duplicate.spec or "无"}, '
                          f'分类：{duplicate.category.name}, 单位：{duplicate.unit}, '
                          f'编号：{duplicate.code}）'
            }
        
        return False, None
