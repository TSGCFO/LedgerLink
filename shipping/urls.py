from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CADShippingViewSet, USShippingViewSet

# Create routers and register our viewsets
cad_router = DefaultRouter()
cad_router.register(r'cad', CADShippingViewSet)

us_router = DefaultRouter()
us_router.register(r'us', USShippingViewSet)

# The API URLs are now determined automatically by the routers
urlpatterns = [
    path('', include(cad_router.urls)),
    path('', include(us_router.urls)),
]
