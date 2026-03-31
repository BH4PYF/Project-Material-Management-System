from django.urls import path
from . import views
from .views import tasks as task_views

urlpatterns = [
    # 登录/登出
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    # 仪表盘
    path('', views.dashboard, name='dashboard'),
    # 项目管理
    path('projects/', views.project_list, name='project_list'),
    path('projects/save/', views.project_save, name='project_save'),
    path('projects/<int:pk>/delete/', views.project_delete, name='project_delete'),
    path('api/projects/<int:pk>/', views.project_detail_api, name='project_detail_api'),
    path('api/projects/check-name/', views.check_project_name, name='check_project_name'),
    # 材料分类
    path('api/categories/', views.category_list_api, name='category_list_api'),
    # 材料管理
    path('materials/', views.material_list, name='material_list'),
    path('materials/save/', views.material_save, name='material_save'),
    path('materials/<int:pk>/delete/', views.material_delete, name='material_delete'),
    path('api/materials/<int:pk>/', views.material_detail_api, name='material_detail_api'),
    path('api/materials/check-duplicate/', views.check_material_duplicate, name='check_material_duplicate'),
    # 供应商管理
    path('suppliers/', views.supplier_list, name='supplier_list'),
    path('suppliers/save/', views.supplier_save, name='supplier_save'),
    path('suppliers/<int:pk>/delete/', views.supplier_delete, name='supplier_delete'),
    path('api/suppliers/<int:pk>/', views.supplier_detail_api, name='supplier_detail_api'),
    path('api/suppliers/check-duplicate/', views.check_supplier_duplicate, name='check_supplier_duplicate'),
    # 采购计划
    path('purchase-plans/', views.purchase_plan_list, name='purchase_plan_list'),
    path('purchase-plans/save/', views.purchase_plan_save, name='purchase_plan_save'),
    path('purchase-plans/<int:pk>/delete/', views.purchase_plan_delete, name='purchase_plan_delete'),
    path('purchase-plans/<int:pk>/approve/', views.purchase_plan_approve, name='purchase_plan_approve'),
    path('purchase-plans/export/', views.export_purchase_plans, name='export_purchase_plans'),
    path('api/purchase-plans/<int:pk>/', views.purchase_plan_detail_api, name='purchase_plan_detail_api'),
    # 发货管理
    path('deliveries/', views.delivery_list, name='delivery_list'),
    path('deliveries/create/', views.delivery_create, name='delivery_create'),
    path('deliveries/<int:pk>/', views.delivery_detail, name='delivery_detail'),
    path('deliveries/<int:pk>/confirm-ship/', views.delivery_confirm_ship, name='delivery_confirm_ship'),
    path('api/deliveries/<int:pk>/', views.delivery_detail_api, name='delivery_detail_api'),
    path('deliveries/<int:pk>/edit/', views.delivery_edit, name='delivery_edit'),
    path('deliveries/<int:pk>/delete/', views.delivery_delete, name='delivery_delete'),
    path('deliveries/export/', views.export_deliveries, name='export_deliveries'),
    # 快速收货
    path('quick-receive/', views.quick_receive, name='quick_receive'),
    path('api/delivery-by-no/', views.get_delivery_by_no, name='get_delivery_by_no'),
    path('quick-receive/confirm/', views.quick_receive_confirm, name='quick_receive_confirm'),
    # 入库管理
    path('inbound/', views.inbound_list, name='inbound_list'),
    path('inbound/save/', views.inbound_save, name='inbound_save'),
    path('inbound/<int:pk>/delete/', views.inbound_delete, name='inbound_delete'),
    path('api/inbound/<int:pk>/', views.inbound_detail_api, name='inbound_detail_api'),
    # 统计报表
    path('reports/', views.report_page, name='report_page'),
    path('reports/project-cost/', views.report_project_cost, name='report_project_cost'),
    path('reports/supplier-cost/', views.report_supplier_cost, name='report_supplier_cost'),
    path('reports/monthly/', views.report_monthly, name='report_monthly'),
    # 图表分析
    path('charts/', views.chart_page, name='chart_page'),
    path('api/chart-data/', views.chart_data_api, name='chart_data_api'),
    path('api/years/', views.get_years_list, name='get_years_list'),
    # Excel 导出/导入
    path('export/', views.export_excel, name='export_excel'),
    path('import/', views.import_excel, name='import_excel'),
    path('import/template/', views.download_import_template, name='download_import_template'),
    # 异步任务
    path('api/tasks/<str:task_id>/status/', task_views.task_status, name='task_status'),
    path('api/export/inventory/', task_views.export_inventory_async, name='export_inventory_async'),
    path('api/export/inbound/', task_views.export_inbound_async, name='export_inbound_async'),
    path('api/export/purchase-plans/', task_views.export_purchase_plans_async, name='export_purchase_plans_async'),
    path('api/export/deliveries/', task_views.export_deliveries_async, name='export_deliveries_async'),
    # 操作日志
    path('logs/', views.log_list, name='log_list'),
    # 性能监控
    path('performance/', views.performance_dashboard, name='performance_dashboard'),
    path('api/performance/stats/', views.api_performance_stats, name='api_performance_stats'),
    # 用户管理
    path('users/', views.user_list, name='user_list'),
    path('users/save/', views.user_save, name='user_save'),
    path('users/<int:pk>/delete/', views.user_delete, name='user_delete'),
    path('users/groups/', views.user_groups, name='user_groups'),
    path('api/users/<int:pk>/', views.user_detail_api, name='user_detail_api'),
    # 个人设置（所有已登录用户）
    path('profile/', views.profile_page, name='profile_page'),
    path('profile/change-password/', views.change_password, name='change_password'),
    path('profile/update/', views.update_profile, name='update_profile'),
    # 系统设置
    path('settings/', views.settings_page, name='settings_page'),
    path('settings/backup/', views.backup_data, name='backup_data'),
    path('settings/restore/', views.restore_data, name='restore_data'),
    path('settings/add-category/', views.add_custom_category, name='add_custom_category'),
    path('settings/delete-category/<int:pk>/', views.delete_category, name='delete_category'),
    path('api/settings/save/', views.save_system_settings, name='save_system_settings'),
    path('api/settings/save-login-security/', views.save_login_security_settings, name='save_login_security_settings'),
    path('api/settings/users/', views.settings_users_api, name='settings_users_api'),
    path('api/settings/logs/', views.settings_logs_api, name='settings_logs_api'),
    path('settings/clear-all-data/', views.clear_all_data, name='clear_all_data'),
    path('settings/init-categories/', views.init_categories, name='init_categories'),
]
