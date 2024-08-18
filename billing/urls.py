from django.urls import path
from .views import InvoiceListView, InvoiceDetailView, ChargeDetailView, UninvoicedChargeListView, AddChargeToInvoiceView

urlpatterns = [
    path('invoices/', InvoiceListView.as_view(), name='invoice_list'),
    path('invoices/<int:pk>/', InvoiceDetailView.as_view(), name='invoice_detail'),
    path('charges/<int:pk>/', ChargeDetailView.as_view(), name='charge_detail'),
    path('uninvoiced-charges/', UninvoicedChargeListView.as_view(), name='uninvoiced_charge_list'),
    path('add-charge-to-invoice/<int:charge_id>/', AddChargeToInvoiceView.as_view(), name='add_charge_to_invoice'),
]
