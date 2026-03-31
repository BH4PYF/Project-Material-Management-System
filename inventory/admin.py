from django.contrib import admin
from .models import (
    Profile, Project, Category, Material, Supplier,
    InboundRecord, PurchasePlan, Delivery, OperationLog,
    SystemSetting,
)

admin.site.site_header = '材料管理系统'
admin.site.site_title = '材料管理后台'


class SoftDeleteAdmin(admin.ModelAdmin):
    """软删除模型管理基类，支持硬删除操作"""
    actions = ['hard_delete_selected', 'restore_selected']

    def hard_delete_selected(self, request, queryset):
        """硬删除选中的记录"""
        count = queryset.count()
        for obj in queryset:
            obj.hard_delete()
        self.message_user(request, f'成功硬删除 {count} 条记录')
    hard_delete_selected.short_description = '硬删除选中记录'

    def restore_selected(self, request, queryset):
        """恢复选中的软删除记录"""
        count = queryset.filter(is_deleted=True).count()
        queryset.filter(is_deleted=True).update(is_deleted=False, deleted_at=None)
        self.message_user(request, f'成功恢复 {count} 条记录')
    restore_selected.short_description = '恢复选中记录'


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'phone', 'supplier_info']
    list_filter = ['role']
    search_fields = ['user__username', 'user__first_name', 'supplier_info__name']
    autocomplete_fields = ['supplier_info']
    list_select_related = ['user', 'supplier_info']


@admin.register(Project)
class ProjectAdmin(SoftDeleteAdmin):
    list_display = ['code', 'name', 'manager', 'status', 'budget', 'is_deleted', 'created_at']
    list_filter = ['status', 'is_deleted']
    search_fields = ['code', 'name']

    def get_queryset(self, request):
        return Project.all_objects.all()


@admin.register(Category)
class CategoryAdmin(SoftDeleteAdmin):
    list_display = ['code', 'name', 'is_deleted']
    list_filter = ['is_deleted']

    def get_queryset(self, request):
        return Category.all_objects.all()


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'category', 'spec', 'unit', 'standard_price', 'safety_stock']
    list_filter = ['category']
    search_fields = ['code', 'name']
    list_select_related = ['category']


@admin.register(Supplier)
class SupplierAdmin(SoftDeleteAdmin):
    list_display = ['code', 'name', 'contact', 'phone', 'credit_rating', 'is_deleted']
    list_filter = ['is_deleted']
    search_fields = ['code', 'name']

    def get_queryset(self, request):
        return Supplier.all_objects.all()


@admin.register(InboundRecord)
class InboundRecordAdmin(SoftDeleteAdmin):
    list_display = ['no', 'date', 'project', 'material', 'quantity', 'unit_price', 'total_amount', 'supplier', 'is_deleted']
    list_filter = ['project', 'date', 'is_deleted']
    search_fields = ['no']

    def get_queryset(self, request):
        return InboundRecord.all_objects.select_related('project', 'material', 'supplier').all()


@admin.register(PurchasePlan)
class PurchasePlanAdmin(SoftDeleteAdmin):
    list_display = ['no', 'project', 'material', 'quantity', 'total_amount', 'status', 'planned_date', 'is_deleted']
    list_filter = ['status', 'project', 'is_deleted']
    search_fields = ['no', 'material__name']

    def get_queryset(self, request):
        return PurchasePlan.all_objects.select_related('project', 'material').all()


@admin.register(Delivery)
class DeliveryAdmin(SoftDeleteAdmin):
    list_display = ['no', 'purchase_plan', 'actual_quantity', 'actual_unit_price', 'actual_total_amount', 'supplier', 'status', 'is_deleted']
    list_filter = ['status', 'shipping_method', 'is_deleted']
    search_fields = ['no']

    def get_queryset(self, request):
        return Delivery.all_objects.select_related('purchase_plan', 'supplier').all()


@admin.register(OperationLog)
class OperationLogAdmin(admin.ModelAdmin):
    list_display = ['time', 'operator', 'module', 'op_type', 'details']
    list_filter = ['module', 'op_type']
    search_fields = ['details']


@admin.register(SystemSetting)
class SystemSettingAdmin(admin.ModelAdmin):
    list_display = ['key', 'value', 'description', 'updated_at']
    search_fields = ['key', 'value']
    list_filter = ['updated_at']
