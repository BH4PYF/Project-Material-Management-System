"""
自定义上下文处理器
为所有模板提供全局变量
"""
from django.core.cache import cache
from inventory.models import SystemSetting

# 哨兵值：区分"缓存中无此 key"和"值确实为空字符串"
_CACHE_MISS = object()


def global_settings(request):
    """
    为所有模板添加全局设置变量（带 5 分钟缓存）
    """
    cached_value = cache.get('global_company_name', _CACHE_MISS)
    if cached_value is not _CACHE_MISS:
        return {'company_name': cached_value}

    # 从数据库查询并缓存（空值也缓存，防止穿透）
    company_name = SystemSetting.get_setting('company_name', '材料管理系统')
    cache.set('global_company_name', company_name, 300)  # 5 分钟

    return {'company_name': company_name}
