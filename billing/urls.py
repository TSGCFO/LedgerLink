from django.urls import path
from .views import GenerateBillingView, ExportBillingView

urlpatterns = [
    path('generate/', GenerateBillingView.as_view(), name='generate_billing'),
    path('export/', ExportBillingView.as_view(), name='export_billing'),
]
