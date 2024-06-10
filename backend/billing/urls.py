from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CustomerViewSet, ServiceViewSet, CustomerServiceViewSet, 
    InsertViewSet, ProductViewSet, ServiceLogViewSet, OrdersViewSet,
    upload_file, download_template, export_products, product_list, OrderImportView
)

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
    path('upload/', upload_file, name='upload_file'),
    path('download-template/', download_template, name='download_template'),
    path('export-products/', export_products, name='export_products'),
    path('products/', product_list, name='product_list'),
    path('import-orders/', OrderImportView.as_view(), name='import-orders'),
]
