from django.urls import path
from .views import InvoiceListView, InvoiceDetailView, ChargeDetailView

urlpatterns = [
    path('invoices/', InvoiceListView.as_view(), name='invoice_list'),
    path('invoices/<int:pk>/', InvoiceDetailView.as_view(), name='invoice_detail'),
    path('charges/<int:pk>/', ChargeDetailView.as_view(), name='charge_detail'),
]
