# orders/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrderViewSet

# Create a router and register our viewset
router = DefaultRouter()
router.register(r'api', OrderViewSet)

app_name = 'orders'

urlpatterns = [
    # DRF router URLs
    path('', include(router.urls)),
]
