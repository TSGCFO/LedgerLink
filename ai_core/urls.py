# ai_core/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api.views import (
    AISystemViewSet,
    FeatureRequestViewSet,
    AIOperationViewSet
)

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'system', AISystemViewSet, basename='ai-system')
router.register(r'features', FeatureRequestViewSet, basename='feature-requests')
router.register(r'operations', AIOperationViewSet, basename='ai-operations')

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('api/', include(router.urls)),
]