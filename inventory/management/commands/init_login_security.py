"""
初始化登录限流配置到系统设置
"""
from django.core.management.base import BaseCommand
from inventory.models import SystemSetting


class Command(BaseCommand):
    help = '初始化登录限流配置到系统设置'

    def handle(self, *args, **options):
        self.stdout.write('正在初始化登录限流配置...')
        
        # 初始化最大尝试次数
        max_attempts, created = SystemSetting.objects.get_or_create(
            key='login_max_attempts',
            defaults={
                'value': '5',
                'description': '最大登录尝试次数'
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('✓ 已创建：最大登录尝试次数 = 5'))
        else:
            self.stdout.write(f'  已存在：最大登录尝试次数 = {max_attempts.value}')
        
        # 初始化锁定时间（秒）
        lockout_seconds, created = SystemSetting.objects.get_or_create(
            key='login_lockout_seconds',
            defaults={
                'value': '300',
                'description': '登录锁定时间（秒）'
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('✓ 已创建：登录锁定时间 = 300 秒（5 分钟）'))
        else:
            self.stdout.write(f'  已存在：登录锁定时间 = {lockout_seconds.value} 秒')
        
        self.stdout.write('\n提示：您可以在 系统管理 -> 系统设置 -> 登录限流配置 中修改这些参数')
