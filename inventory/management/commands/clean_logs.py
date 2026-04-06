from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from inventory.models import OperationLog


class Command(BaseCommand):
    help = '清理超过指定天数的操作日志，默认保留 365 天'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=365,
            help='保留最近多少天的日志（默认 365）',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='仅统计待删除数量，不实际删除',
        )

    def handle(self, *args, **options):
        days = options['days']
        dry_run = options['dry_run']
        cutoff = timezone.now() - timedelta(days=days)

        qs = OperationLog.objects.filter(time__lt=cutoff)
        count = qs.count()

        if count == 0:
            self.stdout.write(self.style.SUCCESS(
                f'没有超过 {days} 天的日志需要清理'
            ))
            return

        if dry_run:
            self.stdout.write(self.style.WARNING(
                f'[dry-run] 将删除 {count} 条超过 {days} 天的日志（截止 {cutoff:%Y-%m-%d %H:%M}）'
            ))
            return

        # 分批删除，避免长事务锁表
        BATCH_SIZE = 5000
        total_deleted = 0
        while True:
            batch_ids = list(
                OperationLog.objects.filter(time__lt=cutoff)
                .values_list('pk', flat=True)[:BATCH_SIZE]
            )
            if not batch_ids:
                break
            deleted, _ = OperationLog.objects.filter(pk__in=batch_ids).delete()
            total_deleted += deleted

        self.stdout.write(self.style.SUCCESS(
            f'已清理 {total_deleted} 条超过 {days} 天的操作日志'
        ))
