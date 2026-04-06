from django.core.management.base import BaseCommand
from django.db import transaction

from inventory.models import Supplier
from inventory.views.utils import create_user_for_supplier


class Command(BaseCommand):
    help = '为所有尚未关联用户的供应商批量创建用户账号'

    def add_arguments(self, parser):
        parser.add_argument(
            '--password',
            default='12345678',
            help='默认密码（默认：12345678）',
        )

    def handle(self, *args, **options):
        password = options['password']
        suppliers = Supplier.objects.all()
        created = 0
        skipped = 0
        errors = []

        for supplier in suppliers:
            with transaction.atomic():
                user, reason = create_user_for_supplier(supplier, password)
                if user:
                    created += 1
                    self.stdout.write(
                        f'  + {supplier.code} {supplier.name} -> 用户 {user.username}'
                    )
                elif reason == '已存在':
                    skipped += 1
                else:
                    errors.append(f'{supplier.code} {supplier.name}: {reason}')

        self.stdout.write('')
        self.stdout.write(f'创建 {created} 个用户，跳过 {skipped} 个（已有用户）')
        if errors:
            self.stderr.write(f'失败 {len(errors)} 个：')
            for e in errors:
                self.stderr.write(f'  ! {e}')
