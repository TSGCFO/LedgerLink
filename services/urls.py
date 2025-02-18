from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ServiceViewSet

# Create a router and register our viewset
router = DefaultRouter()
router.register(r'', ServiceViewSet)

# The API URLs are now determined automatically by the router
urlpatterns = [
    path('', include(router.urls)),
]
