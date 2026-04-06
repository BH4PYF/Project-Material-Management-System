from django.db import transaction
from django.utils import timezone

from inventory.models import Delivery, InboundRecord, PurchasePlan


class DeliveryStateError(ValueError):
    """发货单状态不允许当前操作。"""


def confirm_ship(delivery: Delivery):
    """确认发货并同步采购计划状态。"""
    if delivery.status != Delivery.STATUS_PENDING:
        raise DeliveryStateError('该发货单当前状态不允许确认发货')

    with transaction.atomic():
        delivery.status = Delivery.STATUS_SHIPPED
        delivery.ship_time = timezone.now()
        delivery.save(update_fields=['status', 'ship_time'])

        plan = delivery.purchase_plan
        plan.status = PurchasePlan.STATUS_SHIPPED
        plan.save(update_fields=['status'])


def quick_receive(delivery_id, receive_date, location, remark, operator):
    """快速收货：发货单转入库单。"""
    from inventory.views.utils import generate_no
    
    with transaction.atomic():
        delivery = Delivery.objects.select_for_update().select_related(
            'purchase_plan', 'purchase_plan__project', 'purchase_plan__material', 'supplier'
        ).get(pk=delivery_id)

        if delivery.status == Delivery.STATUS_RECEIVED:
            raise DeliveryStateError('该发货单已收货，无需重复操作')
        if delivery.status != Delivery.STATUS_SHIPPED:
            raise DeliveryStateError('该发货单尚未发货，无法收货')

        inbound = InboundRecord()
        inbound.no = generate_no('IN')
        inbound.project = delivery.purchase_plan.project
        inbound.material = delivery.purchase_plan.material
        inbound.date = receive_date
        inbound.quantity = delivery.actual_quantity
        inbound.unit_price = delivery.actual_unit_price
        inbound.total_amount = delivery.actual_total_amount
        inbound.supplier = delivery.supplier
        inbound.batch_no = delivery.no
        inbound.location = location
        inbound.spec = delivery.purchase_plan.material.spec or ''
        inbound.operator = operator
        inbound.remark = f"快速收货：发货单{delivery.no}。{remark}"
        inbound.save()

        delivery.status = Delivery.STATUS_RECEIVED
        delivery.save(update_fields=['status'])

        # 检查是否所有关联的发货单都已收货（单次 DB 查询）
        plan = delivery.purchase_plan
        all_received = not plan.deliveries.exclude(status=Delivery.STATUS_RECEIVED).exists()

        # 只有当所有发货单都收货后，才更新采购计划状态
        if all_received:
            plan.status = PurchasePlan.STATUS_RECEIVED
            plan.save(update_fields=['status'])

        return inbound, delivery

