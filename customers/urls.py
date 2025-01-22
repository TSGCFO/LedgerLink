from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CustomerListView, CustomerDetailView, CustomerCreateView,
    CustomerUpdateView, CustomerDeleteView, CustomerViewSet
)
from django.views.generic import TemplateView

router = DefaultRouter()
router.register(r'', CustomerViewSet, basename='customers')

app_name = 'customers'

urlpatterns = [
    path('', CustomerListView.as_view(), name='list'),
    path('<int:pk>/', CustomerDetailView.as_view(), name='detail'),
    path('create/', CustomerCreateView.as_view(), name='add'),
    path('<int:pk>/edit/', CustomerUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', CustomerDeleteView.as_view(), name='delete'),
    path('create-success/', TemplateView.as_view(template_name='customers/customer_create_success.html'),
         name='create_success'),

    #   API---------------URLS---------------------
    path('api/', include(router.urls)),

]