"""
性能监控视图
- 慢请求列表
- API 响应时间统计
- 系统性能指标
"""
import time
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.core.cache import cache
from django.db.models import Avg, Max, Min, Count
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.utils import timezone
from datetime import datetime, timedelta

from inventory.models import OperationLog


@staff_member_required
def performance_dashboard(request):
    """性能监控仪表盘"""
    # 获取缓存的慢请求日志
    slow_requests = cache.get('slow_requests_log', [])
    
    # 计算性能指标
    metrics = calculate_performance_metrics()
    
    # 最近的慢请求（最近 24 小时）
    recent_slow = [req for req in slow_requests[:20]]
    
    # 按路径分组的统计
    path_stats = {}
    for req in slow_requests:
        path = req['path']
        if path not in path_stats:
            path_stats[path] = {
                'count': 0,
                'total_duration': 0,
                'max_duration': 0,
            }
        path_stats[path]['count'] += 1
        path_stats[path]['total_duration'] += req['duration']
        path_stats[path]['max_duration'] = max(path_stats[path]['max_duration'], req['duration'])
    
    # 计算平均时长并排序
    path_summary = []
    for path, stats in path_stats.items():
        path_summary.append({
            'path': path,
            'count': stats['count'],
            'avg_duration': stats['total_duration'] / stats['count'],
            'max_duration': stats['max_duration'],
        })
    path_summary.sort(key=lambda x: x['count'], reverse=True)
    
    context = {
        'slow_requests': recent_slow,
        'metrics': metrics,
        'path_summary': path_summary[:10],  # Top 10
        'total_slow_count': len(slow_requests),
    }
    
    return render(request, 'inventory/performance_dashboard.html', context)


def calculate_performance_metrics():
    """计算性能指标"""
    now = timezone.now()
    hour_ago = now - timedelta(hours=1)
    day_ago = now - timedelta(days=1)
    
    # 从操作日志中估算（如果没有专门的性能日志表）
    recent_logs = OperationLog.objects.filter(time__gte=hour_ago)
    day_logs = OperationLog.objects.filter(time__gte=day_ago)
    
    # 获取缓存的慢请求
    slow_requests = cache.get('slow_requests_log', [])
    hour_slow = [r for r in slow_requests if r['timestamp'] > (time.time() - 3600)]
    day_slow = [r for r in slow_requests if r['timestamp'] > (time.time() - 86400)]
    
    metrics = {
        # 请求统计
        'requests_last_hour': recent_logs.count(),
        'requests_last_day': day_logs.count(),
        
        # 慢请求统计
        'slow_requests_last_hour': len(hour_slow),
        'slow_requests_last_day': len(day_slow),
        
        # 平均响应时间（估算）
        'avg_response_time': sum(r['duration'] for r in slow_requests) / len(slow_requests) if slow_requests else 0,
        
        # 最慢请求
        'slowest_request': max(slow_requests, key=lambda x: x['duration']) if slow_requests else None,
    }
    
    return metrics


@staff_member_required
@require_GET
def api_performance_stats(request):
    """API 性能统计（JSON 格式）"""
    # 从缓存获取慢请求数据
    slow_requests = cache.get('slow_requests_log', [])
    
    # 按状态码分组
    status_stats = {}
    for req in slow_requests:
        status = req['status_code']
        if status not in status_stats:
            status_stats[status] = {
                'count': 0,
                'total_duration': 0,
            }
        status_stats[status]['count'] += 1
        status_stats[status]['total_duration'] += req['duration']
    
    # 按用户分组
    user_stats = {}
    for req in slow_requests:
        user = req['user']
        if user not in user_stats:
            user_stats[user] = {
                'count': 0,
                'total_duration': 0,
            }
        user_stats[user]['count'] += 1
        user_stats[user]['total_duration'] += req['duration']
    
    return JsonResponse({
        'total_slow_requests': len(slow_requests),
        'status_code_distribution': status_stats,
        'user_distribution': user_stats,
        'recent_slow_requests': slow_requests[:50],
    })
