# customer_services/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CustomerServiceListView, CustomerServiceDetailView, CustomerServiceCreateView,
    CustomerServiceUpdateView, CustomerServiceDeleteView, get_customer_skus,
    CustomerServiceViewSet
)

app_name = 'customer_services'

# Create a router and register our viewset
router = DefaultRouter()
router.register(r'api', CustomerServiceViewSet)

urlpatterns = [
    # Main CRUD URLs
    path('', CustomerServiceListView.as_view(), name='customer_service_list'),
    path('<int:pk>/', CustomerServiceDetailView.as_view(), name='customer_service_detail'),
    path('new/', CustomerServiceCreateView.as_view(), name='customer_service_create'),
    path('<int:pk>/edit/', CustomerServiceUpdateView.as_view(), name='customer_service_edit'),
    path('<int:pk>/delete/', CustomerServiceDeleteView.as_view(), name='customer_service_delete'),

    # API endpoints
    path('api/customer-skus/<int:customer_id>/', get_customer_skus, name='get_customer_skus'),
    
    # DRF router URLs
    path('', include(router.urls)),
]
