from rest_framework import serializers
from django.contrib.auth.models import Permission, Group
from ..models import Material, Project, Supplier, Category, InboundRecord, PurchasePlan


class CategorySerializer(serializers.ModelSerializer):
    """材料分类序列化器"""
    class Meta:
        model = Category
        fields = ['id', 'name', 'remark']


class MaterialSerializer(serializers.ModelSerializer):
    """材料序列化器"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = Material
        fields = [
            'id', 'code', 'name', 'category', 'category_name', 
            'spec', 'unit', 'standard_price', 'safety_stock', 'remark'
        ]


class ProjectSerializer(serializers.ModelSerializer):
    """项目序列化器"""
    total_inbound = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    
    class Meta:
        model = Project
        fields = [
            'id', 'code', 'name', 'manager', 'location', 'start_date', 
            'end_date', 'budget', 'status', 'remark', 'total_inbound'
        ]


class SupplierSerializer(serializers.ModelSerializer):
    """供应商序列化器"""
    main_type_name = serializers.CharField(source='main_type.name', read_only=True)
    
    class Meta:
        model = Supplier
        fields = [
            'id', 'code', 'name', 'contact', 'phone', 'address', 
            'main_type', 'main_type_name', 'credit_rating', 'start_date', 'remark'
        ]


class InboundRecordSerializer(serializers.ModelSerializer):
    """入库记录序列化器"""
    project_name = serializers.CharField(source='project.name', read_only=True)
    material_name = serializers.CharField(source='material.name', read_only=True)
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    operator_name = serializers.CharField(source='operator.username', read_only=True)
    
    class Meta:
        model = InboundRecord
        fields = [
            'id', 'no', 'project', 'project_name', 'material', 'material_name',
            'date', 'quantity', 'unit_price', 'total_amount', 'supplier', 'supplier_name',
            'batch_no', 'inspector', 'quality_status', 'location', 'spec',
            'operator', 'operator_name', 'operate_time', 'remark'
        ]


class PurchasePlanSerializer(serializers.ModelSerializer):
    """采购计划序列化器"""
    project_name = serializers.CharField(source='project.name', read_only=True)
    material_name = serializers.CharField(source='material.name', read_only=True)
    operator_name = serializers.CharField(source='operator.username', read_only=True)
    
    class Meta:
        model = PurchasePlan
        fields = [
            'id', 'no', 'project', 'project_name', 'material', 'material_name',
            'quantity', 'unit_price', 'total_amount', 'status', 'planned_date',
            'operator', 'operator_name', 'remark'
        ]


class PermissionSerializer(serializers.ModelSerializer):
    """权限序列化器"""
    app_label = serializers.CharField(source='content_type.app_label', read_only=True)
    model = serializers.CharField(source='content_type.model', read_only=True)
    
    class Meta:
        model = Permission
        fields = ['id', 'codename', 'name', 'app_label', 'model']


class GroupPermissionSerializer(serializers.ModelSerializer):
    """用户组权限序列化器"""
    permissions = PermissionSerializer(many=True, read_only=True)
    
    class Meta:
        model = Group
        fields = ['id', 'name', 'permissions']
