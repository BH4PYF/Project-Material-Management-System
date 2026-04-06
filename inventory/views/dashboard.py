from datetime import date
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.db.models import Sum, Count
from django.shortcuts import render

from ..models import Project, Material, Supplier, InboundRecord


@login_required
def dashboard(request):
    today = date.today()
    cache_key = f'dashboard_stats_{today}'
    stats = cache.get(cache_key)

    if stats is None:
        # 使用聚合查询代替全表查询
        projects_count = Project.objects.count()
        active_projects_count = Project.objects.filter(status='active').count()
        materials_count = Material.objects.count()
        suppliers_count = Supplier.objects.count()

        # 获取今日入库统计（合并为一次查询）
        today_stats = InboundRecord.objects.filter(date=today).aggregate(
            count=Count('id'),
            total=Sum('total_amount'),
        )

        stats = {
            'projects_count': projects_count,
            'active_projects_count': active_projects_count,
            'materials_count': materials_count,
            'suppliers_count': suppliers_count,
            'today_inbound_count': today_stats['count'],
            'today_inbound_amount': today_stats['total'] or 0,
        }
        # 缓存 60 秒，平衡实时性与性能
        cache.set(cache_key, stats, 60)

    # 只查询今日入库记录（限制数量）
    recent_inbounds = InboundRecord.objects.select_related('project', 'material', 'supplier').filter(
        date=today
    ).order_by('-operate_time')[:20]

    # 只返回前 50 条记录用于模板展示（避免大数据量）
    projects = Project.objects.filter(status__in=['active', 'pending']).order_by('-status', 'code')[:50]
    materials = Material.objects.select_related('category').all().order_by('code')[:100]
    suppliers = Supplier.objects.all().order_by('code')[:50]

    return render(request, 'inventory/dashboard.html', {
        'recent_inbounds': recent_inbounds,
        'projects': projects,
        'materials': materials,
        'suppliers': suppliers,
        'today': today,
        'stats': stats,
    })
