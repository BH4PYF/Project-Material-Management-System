"""
自定义中间件
- ProfileMiddleware: 性能分析（开发环境）
- SlowRequestMiddleware: 慢请求记录（生产环境）
"""
import time
import logging
from collections import deque
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger('inventory')


class ProfileMiddleware:
    """
    性能分析中间件（仅开发环境）
    记录每个请求的 SQL 查询数量和执行时间
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # 记录开始时间
        start_time = time.time()
        
        # 处理请求
        response = self.get_response(request)
        
        # 计算执行时间
        duration = time.time() - start_time
        
        # 从 django-debug-toolbar 获取 SQL 统计（如果可用）
        try:
            from debug_toolbar.panels.sql.tracking import SQLQueryTriggered
            # 这个信息会由 toolbar 自动显示
        except ImportError:
            pass
        
        # 记录慢请求（超过 1 秒）
        if duration > 1.0:
            logger.warning(
                '慢请求：%s %s - %.3fs', request.method, request.path, duration,
                extra={
                    'method': request.method,
                    'path': request.path,
                    'duration': duration,
                    'user': getattr(request.user, 'username', 'anonymous'),
                }
            )
        
        # 在响应头中添加执行时间（便于前端调试）
        response['X-Execution-Time'] = f'{duration:.3f}s'
        
        return response


class SlowRequestMiddleware:
    """
    慢请求记录中间件（生产环境）
    记录超过阈值的请求到数据库和日志
    """
    
    SLOW_THRESHOLD = float(getattr(settings, 'SLOW_REQUEST_THRESHOLD', '2.0'))  # 默认 2 秒
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # 记录开始时间
        start_time = time.time()
        
        # 处理请求
        response = self.get_response(request)
        
        # 计算执行时间
        duration = time.time() - start_time
        
        # 只记录慢请求
        if duration > self.SLOW_THRESHOLD:
            self._log_slow_request(request, duration, response.status_code)
        
        return response
    
    def _log_slow_request(self, request, duration, status_code):
        """记录慢请求到日志和缓存"""
        log_entry = {
            'timestamp': time.time(),
            'method': request.method,
            'path': request.path,
            'duration': duration,
            'status_code': status_code,
            'user': getattr(request.user, 'username', 'anonymous') if hasattr(request, 'user') else 'anonymous',
            'ip': self._get_client_ip(request),
        }
        
        # 记录到日志
        logger.warning(
            '慢请求：%s %s - %.3fs (状态码：%d)', request.method, request.path, duration, status_code,
            extra=log_entry
        )
        
        # 缓存最近的慢请求（用于统计页面）
        self._cache_slow_request(log_entry)
    
    def _get_client_ip(self, request):
        """获取客户端 IP（仅信任来自可信代理的 X-Forwarded-For）"""
        remote_addr = request.META.get('REMOTE_ADDR', '')
        trusted_proxies = getattr(settings, 'TRUSTED_PROXIES', [])

        if trusted_proxies and remote_addr in trusted_proxies:
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                first_ip = x_forwarded_for.split(',')[0].strip()
                if first_ip:
                    return first_ip

        return remote_addr
    
    def _cache_slow_request(self, log_entry):
        """缓存最近的慢请求"""
        cache_key = 'slow_requests_log'
        slow_requests = cache.get(cache_key)

        if not isinstance(slow_requests, deque):
            # 首次或缓存过期时创建新的 deque
            slow_requests = deque(slow_requests or [], maxlen=100)

        slow_requests.appendleft(log_entry)

        # 缓存 1 小时
        cache.set(cache_key, slow_requests, 3600)
