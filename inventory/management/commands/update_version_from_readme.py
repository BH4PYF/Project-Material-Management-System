"""
从 README.md 文件读取版本号并更新到系统设置
"""
from django.core.management.base import BaseCommand, CommandError
import re
import os
from inventory.models import SystemSetting


class Command(BaseCommand):
    help = '从 README.md 文件读取版本号并更新到系统设置'

    def handle(self, *args, **options):
        self.stdout.write('正在读取 README.md 文件...')
        
        # 读取 README.md 文件
        readme_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'README.md')
        
        if not os.path.exists(readme_path):
            raise CommandError(f'找不到 README.md 文件：{readme_path}')
        
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 从徽章中提取 Django 版本（修复正则表达式）
        django_version_match = re.search(r'\[Django\].*?-([\d.]+)', content)
        python_version_match = re.search(r'\[Python\].*?-([\d.]+)', content)
        
        if django_version_match:
            django_version = django_version_match.group(1)
            self.stdout.write(f'✓ 读取到 Django 版本：{django_version}')
        else:
            django_version = '未知'
            self.stdout.write('⚠ 未找到 Django 版本信息')
        
        if python_version_match:
            python_version = python_version_match.group(1)
            self.stdout.write(f'✓ 读取到 Python 版本：{python_version}')
        else:
            python_version = '未知'
            self.stdout.write('⚠ 未找到 Python 版本信息')
        
        # 尝试从标题或其他位置提取系统版本号
        # 例如：# 材料管理系统 V1.8
        version_match = re.search(r'材料管理系统\s*[Vv](\d+\.\d+(?:\.\d+)?)', content)
        if version_match:
            system_version = version_match.group(1)
            self.stdout.write(f'✓ 读取到系统版本：V{system_version}')
        else:
            # 如果没有明确的系统版本号，使用 Django 版本作为参考
            system_version = django_version
            self.stdout.write(f'ℹ 使用 Django 版本作为系统版本参考：{system_version}')
        
        # 更新系统设置
        company_name_setting = SystemSetting.get_setting('company_name', '材料管理系统')
        
        # 构建新的公司名称（包含版本号）
        new_company_name = f'材料管理系统 V{system_version}'
        
        # 询问是否更新
        self.stdout.write('\n当前系统设置:')
        self.stdout.write(f'  company_name: {company_name_setting}')
        
        self.stdout.write(f'\n将更新为:')
        self.stdout.write(f'  company_name: {new_company_name}')
        
        # 直接更新（如果需要确认，可以添加交互逻辑）
        SystemSetting.set_setting('company_name', new_company_name)
        
        self.stdout.write(self.style.SUCCESS('\n✓ 系统设置已更新成功!'))
        self.stdout.write(f'\n提示：请刷新页面查看新的系统名称')
