from django.urls import path
from .views import CustomerListView, CustomerDetailView, CustomerCreateView, CustomerUpdateView, CustomerDeleteView

app_name = 'customers'  # Add this line to define the namespace

urlpatterns = [
    path('', CustomerListView.as_view(), name='customer_list'),
    path('<int:pk>/', CustomerDetailView.as_view(), name='customer_detail'),
    path('add/', CustomerCreateView.as_view(), name='customer_add'),
    path('<int:pk>/edit/', CustomerUpdateView.as_view(), name='customer_edit'),
    path('customer/<int:pk>/delete/', CustomerDeleteView.as_view(), name='customer_delete'),

]
