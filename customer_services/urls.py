from django.urls import path
from .views import (
    CustomerServiceListView, CustomerServiceDetailView, CustomerServiceCreateView,
    CustomerServiceUpdateView, CustomerServiceDeleteView
)

urlpatterns = [
    path('', CustomerServiceListView.as_view(), name='customer_service_list'),
    path('customer_service/<int:pk>/', CustomerServiceDetailView.as_view(), name='customer_service_detail'),
    path('customer_service/new/', CustomerServiceCreateView.as_view(), name='customer_service_create'),
    path('customer_service/<int:pk>/edit/', CustomerServiceUpdateView.as_view(), name='customer_service_update'),
    path('customer_service/<int:pk>/delete/', CustomerServiceDeleteView.as_view(), name='customer_service_delete'),
]
