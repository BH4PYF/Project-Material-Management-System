"""
自定义模板标签
"""
from django import template
from datetime import datetime, timezone

register = template.Library()


@register.filter
def to_datetime(timestamp, format_string='%Y-%m-%d %H:%M:%S'):
    """将时间戳转换为日期格式（使用 UTC 时区）"""
    try:
        return datetime.fromtimestamp(float(timestamp), tz=timezone.utc).strftime(format_string)
    except (ValueError, TypeError, OSError):
        return 'N/A'
