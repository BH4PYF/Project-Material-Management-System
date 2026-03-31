from django.conf import settings
from django.core.cache import cache

from inventory.models import SystemSetting


def get_client_ip(request):
    """获取客户端 IP，仅信任来自可信代理的 X-Forwarded-For。"""
    remote_addr = request.META.get('REMOTE_ADDR', '')
    trusted_proxies = getattr(settings, 'TRUSTED_PROXIES', [])

    if trusted_proxies and remote_addr in trusted_proxies:
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            first_ip = x_forwarded_for.split(',')[0].strip()
            if first_ip:
                return first_ip
    return remote_addr


def _user_key(username, ip_address=None):
    if ip_address:
        return f'login_attempts:{username}:{ip_address}'
    return f'login_attempts:{username}'


def _ip_key(ip_address):
    return f'login_attempts:ip:{ip_address}'


def get_login_max_attempts():
    cached_value = cache.get('LOGIN_MAX_ATTEMPTS')
    if cached_value is not None:
        return int(cached_value)

    value = SystemSetting.get_setting('login_max_attempts', '')
    if value:
        try:
            int_value = int(value)
            cache.set('LOGIN_MAX_ATTEMPTS', int_value, 300)
            return int_value
        except (ValueError, TypeError):
            pass

    return getattr(settings, 'LOGIN_MAX_ATTEMPTS', 5)


def get_login_lockout_seconds():
    cached_value = cache.get('LOGIN_LOCKOUT_SECONDS')
    if cached_value is not None:
        return int(cached_value)

    value = SystemSetting.get_setting('login_lockout_seconds', '')
    if value:
        try:
            int_value = int(value)
            cache.set('LOGIN_LOCKOUT_SECONDS', int_value, 300)
            return int_value
        except (ValueError, TypeError):
            pass

    return getattr(settings, 'LOGIN_LOCKOUT_SECONDS', 300)


def get_login_attempts(username, ip_address):
    user_attempts = cache.get(_user_key(username, ip_address), 0)
    if getattr(settings, 'TESTING', False):
        return user_attempts
    ip_attempts = cache.get(_ip_key(ip_address), 0)
    return max(user_attempts, ip_attempts)


def increment_login_attempts(username, ip_address):
    lockout_seconds = get_login_lockout_seconds()

    user_key = _user_key(username, ip_address)
    user_attempts = cache.get(user_key, 0) + 1
    cache.set(user_key, user_attempts, lockout_seconds)

    ip_key = _ip_key(ip_address)
    ip_attempts = cache.get(ip_key, 0) + 1
    cache.set(ip_key, ip_attempts, lockout_seconds)

    return max(user_attempts, ip_attempts)


def clear_login_attempts(username, ip_address):
    cache.delete(_user_key(username, ip_address))
    cache.delete(_ip_key(ip_address))

