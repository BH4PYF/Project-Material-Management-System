"""
删除材料档案中的重复记录
使用方法：python manage.py remove_duplicate_materials
"""
from django.core.management.base import BaseCommand
from inventory.models import Material
from django.db.models import Count, Min


class Command(BaseCommand):
    help = '删除材料档案中名称 + 规格相同的重复记录，保留 ID 最小的记录'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='仅显示将要删除的记录，不实际执行删除',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        # 查找所有名称 + 规格相同的重复材料
        duplicates = Material.objects.values('name', 'spec').annotate(
            count=Count('id'),
            min_id=Min('id')
        ).filter(count__gt=1)

        if not duplicates:
            self.stdout.write(self.style.SUCCESS('✅ 没有发现重复材料！'))
            return

        self.stdout.write(f'\n📋 发现 {len(duplicates)} 组重复材料\n')
        
        deleted_count = 0
        
        for dup in duplicates:
            name = dup['name']
            spec = dup['spec']
            min_id = dup['min_id']
            
            # 获取这组重复材料的所有记录（除了 ID 最小的那条）
            to_delete = Material.objects.filter(name=name, spec=spec).exclude(id=min_id)
            
            # 获取要删除的记录信息用于日志
            delete_list = list(to_delete.values_list('code', 'id'))
            
            count = to_delete.count()
            
            # 获取保留的记录信息
            keeper = Material.objects.get(id=min_id)
            
            if dry_run:
                self.stdout.write(f'⚠️  【预览】{name} - {spec or "(无规格)"}')
                self.stdout.write(f'   将保留：ID:{min_id:3d} | {keeper.code}')
                self.stdout.write(f'   将删除：{count} 条记录')
                for code, del_id in delete_list:
                    self.stdout.write(f'          - ID:{del_id:3d} | {code}')
                deleted_count += count
            else:
                # 执行删除
                to_delete.delete()
                deleted_count += count
                
                self.stdout.write(f'✓ 【{name} - {spec or "(无规格)"}】')
                self.stdout.write(f'  保留：ID:{min_id:3d} | {keeper.code}')
                self.stdout.write(f'  删除：{count} 条记录')
                for code, del_id in delete_list:
                    self.stdout.write(f'       - ID:{del_id:3d} | {code}')
            
            self.stdout.write()
        
        self.stdout.write('=' * 60)
        if dry_run:
            self.stdout.write(self.style.WARNING(
                f'⚠️  预览模式：共发现 {deleted_count} 条记录待删除'
            ))
        else:
            self.stdout.write(self.style.SUCCESS(
                f'✅ 删除完成！共删除 {deleted_count} 条重复记录'
            ))
        self.stdout.write('=' * 60)

        # 验证是否还有重复
        if not dry_run:
            remaining = Material.objects.values('name', 'spec').annotate(
                count=Count('id')
            ).filter(count__gt=1)

            if remaining:
                self.stdout.write(self.style.ERROR(
                    f'\n⚠️ 警告：仍有 {len(remaining)} 组重复材料未删除！'
                ))
            else:
                self.stdout.write(self.style.SUCCESS('\n✅ 所有重复材料已清除完毕！'))
