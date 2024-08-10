# products/urls.py
from django.urls import path
from .views import ProductListView, ProductDetailView, ProductCreateView, ProductUpdateView, ProductUploadView

urlpatterns = [
    path('', ProductListView.as_view(), name='product_list'),
    path('<int:pk>/', ProductDetailView.as_view(), name='product_detail'),
    path('add/', ProductCreateView.as_view(), name='product_add'),
    path('<int:pk>/edit/', ProductUpdateView.as_view(), name='product_edit'),
    path('upload/', ProductUploadView.as_view(), name='product_upload'),

]
