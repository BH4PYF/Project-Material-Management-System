from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST

from django.core.paginator import Paginator

from ..models import Category, Material, InboundRecord
from ..services import MaterialService
from .utils import admin_required, log_operation, parse_positive_decimal, validate_required_fields, combined_permission_required


@combined_permission_required(perm='inventory.view_category', roles=['admin', 'management'])
@require_GET
def category_list_api(request):
    cats = Category.objects.all().order_by('code')
    data = [{'id': c.pk, 'code': c.code, 'name': c.name} for c in cats]
    return JsonResponse(data, safe=False)


@combined_permission_required(perm='inventory.view_material', roles=['admin', 'management'])
def material_list(request):
    q = request.GET.get('q', '')
    cat_id = request.GET.get('category', '')
    
    # 使用服务层获取材料列表和统计信息
    materials_with_stats = MaterialService.get_materials_with_statistics(
        category_id=cat_id if cat_id else None,
        search_query=q
    )
    
    # 分页处理
    paginator = Paginator(materials_with_stats, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    categories = Category.objects.all().order_by('code')
    return render(request, 'inventory/material_list.html', {
        'material_data': page_obj, 'categories': categories, 'q': q, 'cat_id': cat_id,
        'page_obj': page_obj,
    })


@combined_permission_required(perm='inventory.change_material', roles=['admin', 'management'])
def material_save(request):
    if request.method == 'POST':
        pk = request.POST.get('id')
        name = request.POST.get('name', '').strip()
        category_id = request.POST.get('category_id')
        spec = request.POST.get('spec', '').strip()
        unit = request.POST.get('unit', '').strip()
        
        # 验证必填字段
        err = validate_required_fields(request.POST, {
            'name': '材料名称不能为空',
            'category_id': '材料分类不能为空',
            'unit': '计量单位不能为空',
        })
        if err:
            return JsonResponse({'error': err}, status=400)
        
        standard_price, err = parse_positive_decimal(request.POST.get('standard_price') or '0', '标准单价', allow_zero=True)
        if err:
            return JsonResponse({'error': err}, status=400)
        safety_stock, err = parse_positive_decimal(request.POST.get('safety_stock') or '0', '安全库存量', allow_zero=True)
        if err:
            return JsonResponse({'error': err}, status=400)
        
        # 准备数据
        data = {
            'name': name,
            'category_id': category_id,
            'spec': spec,
            'unit': unit,
            'standard_price': standard_price,
            'safety_stock': safety_stock,
            'remark': request.POST.get('remark', '')
        }
        
        # 使用服务层处理创建或更新
        if pk:
            material, error = MaterialService.update_material(int(pk), data)
            action = 'update'
        else:
            material, error = MaterialService.create_material(data)
            action = 'create'
        
        if error:
            return JsonResponse({'error': error}, status=400)
        
        log_operation(request.user, '材料档案', action, f'{"新增" if action == "create" else "修改"}材料 {material.code} {material.name}', material.code)
        return JsonResponse({'success': True, 'message': '保存成功'})
    return redirect('material_list')


@combined_permission_required(perm='inventory.delete_material', roles=['admin', 'management'])
@require_POST
def material_delete(request, pk):
    success, error = MaterialService.delete_material(int(pk))
    if not success:
        return JsonResponse({'error': error}, status=400)
    
    # 获取材料代码用于日志
    material = Material.objects.get(pk=pk)
    log_operation(request.user, '材料档案', 'delete', f'删除材料 {material.code}', material.code)
    return JsonResponse({'success': True})


@combined_permission_required(perm='inventory.view_material', roles=['admin', 'management'])
@require_GET
def material_detail_api(request, pk):
    obj = get_object_or_404(Material, pk=pk)
    data = {
        'id': obj.pk, 'code': obj.code, 'name': obj.name, 'category_id': obj.category_id,
        'spec': obj.spec, 'unit': obj.unit, 'standard_price': str(obj.standard_price),
        'safety_stock': str(obj.safety_stock), 'remark': obj.remark,
        'total_inbound': str(obj.get_total_inbound()),
        'avg_cost': str(obj.get_weighted_avg_cost()),
    }
    return JsonResponse(data)


@combined_permission_required(perm='inventory.view_material', roles=['admin', 'management'])
@require_GET
def check_material_duplicate(request):
    """检查材料是否重复（用于前端实时查重）"""
    name = request.GET.get('name', '').strip()
    spec = request.GET.get('spec', '').strip()
    exclude_id = request.GET.get('id')
    
    exists, duplicate_info = MaterialService.check_material_duplicate(
        name, spec, int(exclude_id) if exclude_id else None
    )
    
    if exists and duplicate_info:
        return JsonResponse({
            'exists': True,
            'code': duplicate_info['code'],
            'message': duplicate_info['message']
        })
    else:
        return JsonResponse({'exists': False})
