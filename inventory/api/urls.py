from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    CategoryViewSet, MaterialViewSet, ProjectViewSet,
    SupplierViewSet, InboundRecordViewSet, PurchasePlanViewSet,
    update_group
)

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'materials', MaterialViewSet, basename='material')
router.register(r'projects', ProjectViewSet, basename='project')
router.register(r'suppliers', SupplierViewSet, basename='supplier')
router.register(r'inbound-records', InboundRecordViewSet, basename='inbound-record')
router.register(r'purchase-plans', PurchasePlanViewSet, basename='purchase-plan')

urlpatterns = [
    path('', include(router.urls)),
    path('groups/<int:group_id>/', update_group, name='update_group'),
]
