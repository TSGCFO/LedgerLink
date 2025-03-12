from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create a router and register viewsets
router = DefaultRouter()
router.register(r'reports', views.BillingReportViewSet)

# URL patterns for the billing API
urlpatterns = [
    path('', include(router.urls)),
]