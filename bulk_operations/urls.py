# bulk_operations/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'templates', views.BulkOperationViewSet, basename='bulk-operations')

urlpatterns = [
    path('', include(router.urls)),
    path('templates/<str:template_type>/download/',
         views.TemplateDownloadView.as_view(), name='template-download'),
    path('import/<str:template_type>/',
         views.BulkImportView.as_view(), name='bulk-import'),
]
