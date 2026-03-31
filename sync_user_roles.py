import django
import os

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'material_system.settings')
django.setup()

from django.contrib.auth.models import User, Group
from inventory.models import Profile

print("开始同步用户角色和用户组...")
print("-" * 60)

# 创建角色代码到名称的映射
role_code_to_name = {role_code: role_name for role_code, role_name in Profile.ROLE_CHOICES}

# 获取所有用户
users = User.objects.select_related('profile').all()

for user in users:
    if not hasattr(user, 'profile'):
        print(f"用户 {user.username} 没有profile，跳过")
        continue
    
    role = user.profile.role
    print(f"处理用户: {user.username}, 角色: {role}")
    
    # 移除用户的所有用户组
    user.groups.clear()
    
    # 如果是预定义角色，尝试将用户添加到对应的用户组
    if role in role_code_to_name:
        role_name = role_code_to_name[role]
        try:
            # 查找名称匹配的用户组
            group = Group.objects.get(name=role_name)
            user.groups.add(group)
            print(f"  ✓ 添加到用户组: {role_name}")
        except Group.DoesNotExist:
            print(f"  ✗ 用户组 {role_name} 不存在")

print("-" * 60)
print("同步完成！")