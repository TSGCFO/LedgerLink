from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CustomerViewSet, ServiceViewSet, CustomerServiceViewSet, InsertViewSet, ProductViewSet, ServiceLogViewSet, OrdersViewSet

router = DefaultRouter()
router.register(r'customers', CustomerViewSet)
router.register(r'services', ServiceViewSet)
router.register(r'customer-services', CustomerServiceViewSet)
router.register(r'inserts', InsertViewSet)
router.register(r'products', ProductViewSet)
router.register(r'service-logs', ServiceLogViewSet)
router.register(r'orders', OrdersViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
