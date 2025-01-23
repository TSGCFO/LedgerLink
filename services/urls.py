# services/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ServiceListView, ServiceDetailView, ServiceCreateView,
    ServiceUpdateView, ServiceDeleteView, ServiceViewSet
)

app_name = 'services'

# Create a router and register our viewset
router = DefaultRouter()
router.register(r'api', ServiceViewSet)

# URL patterns for both template views and API endpoints
urlpatterns = [
    # Template-based views
    path('', ServiceListView.as_view(), name='service_list'),
    path('service/<int:pk>/', ServiceDetailView.as_view(), name='service_detail'),
    path('service/new/', ServiceCreateView.as_view(), name='service_create'),
    path('service/<int:pk>/edit/', ServiceUpdateView.as_view(), name='service_update'),
    path('service/<int:pk>/delete/', ServiceDeleteView.as_view(), name='service_delete'),
    
    # API endpoints
    path('', include(router.urls)),
]
