from django.urls import path
from .views import OrderListView, OrderDetailView, OrderCreateView, OrderUpdateView, OrderDeleteView

app_name = 'orders'  # Add namespace

urlpatterns = [
    path('', OrderListView.as_view(), name='order_list'),
    path('order/<int:pk>/', OrderDetailView.as_view(), name='order_detail'),
    path('order/new/', OrderCreateView.as_view(), name='order_create'),
    path('order/<int:pk>/edit/', OrderUpdateView.as_view(), name='order_update'),
    path('order/<int:pk>/delete/', OrderDeleteView.as_view(), name='order_delete'),
]
