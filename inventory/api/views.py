from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django_filters.rest_framework import FilterSet, filters
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import Group

from ..models import Material, Project, Supplier, Category, InboundRecord, PurchasePlan
from ..services import MaterialService, ProjectService
from .serializers import (
    MaterialSerializer, ProjectSerializer, SupplierSerializer,
    CategorySerializer, InboundRecordSerializer, PurchasePlanSerializer,
    GroupPermissionSerializer
)


class AdminRequiredPermission(permissions.BasePermission):
    """管理员权限验证"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and hasattr(request.user, 'profile') and request.user.profile.role == 'admin'


class MaterialFilter(FilterSet):
    """材料过滤"""
    category = filters.NumberFilter(field_name='category_id')
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')
    code = filters.CharFilter(field_name='code', lookup_expr='icontains')
    
    class Meta:
        model = Material
        fields = ['category', 'name', 'code']


class ProjectFilter(FilterSet):
    """项目过滤"""
    status = filters.CharFilter(field_name='status')
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')
    code = filters.CharFilter(field_name='code', lookup_expr='icontains')
    
    class Meta:
        model = Project
        fields = ['status', 'name', 'code']


class SupplierFilter(FilterSet):
    """供应商过滤"""
    main_type = filters.NumberFilter(field_name='main_type_id')
    credit_rating = filters.CharFilter(field_name='credit_rating')
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')
    
    class Meta:
        model = Supplier
        fields = ['main_type', 'credit_rating', 'name']


class CategoryViewSet(viewsets.ModelViewSet):
    """分类视图集"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AdminRequiredPermission]
    filterset_fields = ['name']
    search_fields = ['name']


class MaterialViewSet(viewsets.ModelViewSet):
    """材料视图集"""
    queryset = Material.objects.all().select_related('category')
    serializer_class = MaterialSerializer
    permission_classes = [AdminRequiredPermission]
    filterset_class = MaterialFilter
    search_fields = ['name', 'code', 'spec']
    ordering_fields = ['code', 'name', 'standard_price']
    
    def list(self, request, *args, **kwargs):
        """获取材料列表（包含统计信息）"""
        search_query = request.query_params.get('search', '')
        queryset = self.filter_queryset(self.get_queryset())
        
        # 使用服务层获取带统计信息的材料列表
        materials_with_stats = MaterialService.get_materials_with_statistics(search_query=search_query)
        
        page = self.paginate_queryset(materials_with_stats)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(materials_with_stats, many=True)
        return Response(serializer.data)
    
    def create(self, request, *args, **kwargs):
        """创建材料"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # 使用服务层创建材料
        material, error = MaterialService.create_material(serializer.validated_data)
        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = self.get_serializer(material)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def update(self, request, *args, **kwargs):
        """更新材料"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        
        # 使用服务层更新材料
        material, error = MaterialService.update_material(instance.id, serializer.validated_data)
        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = self.get_serializer(material)
        return Response(serializer.data)
    
    def destroy(self, request, *args, **kwargs):
        """删除材料"""
        instance = self.get_object()
        
        # 使用服务层删除材料
        success, error = MaterialService.delete_material(instance.id)
        if not success:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProjectViewSet(viewsets.ModelViewSet):
    """项目视图集"""
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [AdminRequiredPermission]
    filterset_class = ProjectFilter
    search_fields = ['name', 'code', 'manager']
    ordering_fields = ['code', 'name', 'start_date']
    
    def list(self, request, *args, **kwargs):
        """获取项目列表（包含统计信息）"""
        search_query = request.query_params.get('search', '')
        status_filter = request.query_params.get('status')
        
        # 使用服务层获取带统计信息的项目列表
        projects_with_stats = ProjectService.get_projects_with_statistics(
            search_query=search_query,
            status_filter=status_filter
        )
        
        page = self.paginate_queryset(projects_with_stats)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(projects_with_stats, many=True)
        return Response(serializer.data)
    
    def create(self, request, *args, **kwargs):
        """创建项目"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # 使用服务层创建项目
        project, error = ProjectService.create_project(serializer.validated_data)
        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = self.get_serializer(project)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def update(self, request, *args, **kwargs):
        """更新项目"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        
        # 使用服务层更新项目
        project, error = ProjectService.update_project(instance.id, serializer.validated_data)
        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = self.get_serializer(project)
        return Response(serializer.data)
    
    def destroy(self, request, *args, **kwargs):
        """删除项目"""
        instance = self.get_object()
        
        # 使用服务层删除项目
        success, error = ProjectService.delete_project(instance.id)
        if not success:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(status=status.HTTP_204_NO_CONTENT)


class SupplierViewSet(viewsets.ModelViewSet):
    """供应商视图集"""
    queryset = Supplier.objects.all().select_related('main_type')
    serializer_class = SupplierSerializer
    permission_classes = [AdminRequiredPermission]
    filterset_class = SupplierFilter
    search_fields = ['name', 'code', 'contact', 'phone']
    ordering_fields = ['code', 'name', 'credit_rating']


class InboundRecordViewSet(viewsets.ReadOnlyModelViewSet):
    """入库记录视图集（只读）"""
    queryset = InboundRecord.objects.all().select_related(
        'project', 'material', 'supplier', 'operator'
    )
    serializer_class = InboundRecordSerializer
    permission_classes = [AdminRequiredPermission]
    filterset_fields = ['project', 'material', 'supplier', 'date']
    search_fields = ['no', 'batch_no', 'inspector']
    ordering_fields = ['no', 'date', 'total_amount']


class PurchasePlanViewSet(viewsets.ModelViewSet):
    """采购计划视图集"""
    queryset = PurchasePlan.objects.all().select_related(
        'project', 'material', 'operator'
    )
    serializer_class = PurchasePlanSerializer
    permission_classes = [AdminRequiredPermission]
    filterset_fields = ['project', 'material', 'status']
    search_fields = ['no', 'remark']
    ordering_fields = ['no', 'planned_date', 'total_amount']


@api_view(['PUT'])
@permission_classes([AdminRequiredPermission])
def update_group(request, group_id):
    """更新用户组的API端点"""
    group = get_object_or_404(Group, pk=group_id)
    name = request.data.get('name')

    if not name:
        return Response({'success': False, 'message': '用户组名称不能为空'}, status=status.HTTP_400_BAD_REQUEST)

    # 检查名称是否已存在
    if Group.objects.filter(name=name).exclude(id=group_id).exists():
        return Response({'success': False, 'message': '用户组名称已存在'}, status=status.HTTP_400_BAD_REQUEST)

    # 更新用户组名称
    group.name = name
    group.save()

    return Response({'success': True, 'message': '用户组更新成功'})
