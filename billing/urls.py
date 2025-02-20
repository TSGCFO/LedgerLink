from django.urls import path
from .views import BillingReportView, GenerateReportAPIView, BillingReportListView

app_name = 'billing'

urlpatterns = [
    path('report/', BillingReportView.as_view(), name='report'),
    path('api/reports/', BillingReportListView.as_view(), name='report_list'),
    path('api/generate-report/', GenerateReportAPIView.as_view(), name='generate_report'),
]
