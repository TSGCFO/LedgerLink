# billing/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('generate-billing/', views.generate_billing_view, name='generate_billing'),
    path('invoice/<int:invoice_id>/', views.invoice_detail_view, name='invoice_detail'),
    path('invoice-list/', views.invoice_list_view, name='invoice_list'),
    path('export-report/', views.export_report_view, name='export_report'),
]
