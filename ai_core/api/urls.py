# ai_core/api/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AISystemViewSet,
    FeatureRequestViewSet,
    AIOperationViewSet, FeatureImplementationViewSet

)

router = DefaultRouter()
router.register(r'system', AISystemViewSet, basename='ai-system')
router.register(r'features', FeatureRequestViewSet, basename='feature-requests')
router.register(r'operations', AIOperationViewSet, basename='ai-operations')
router.register(r'feature-implementations', FeatureImplementationViewSet, basename='feature-implementations')

urlpatterns = [
    path('', include(router.urls)),
]