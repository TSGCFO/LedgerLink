from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.conf import settings
from django.views.generic import TemplateView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

# Swagger/OpenAPI documentation setup
schema_view = get_schema_view(
    openapi.Info(
        title="LedgerLink API",
        default_version='v1',
        description="API documentation for LedgerLink application",
        terms_of_service="https://www.ledgerlink.com/terms/",
        contact=openapi.Contact(email="contact@ledgerlink.com"),
        license=openapi.License(name="Proprietary"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

# API URL patterns
api_patterns = [
    # Authentication endpoints
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/token/verify/', TokenVerifyView.as_view(), name='token_verify'),

    # App endpoints
    path('customers/', include('customers.urls')),
    path('customer-services/', include('customer_services.urls')),
    path('orders/', include('orders.urls')),
    path('products/', include('products.urls')),
    path('billing/', include('billing.urls')),
    path('services/', include('services.urls')),
    path('shipping/', include('shipping.urls')),
    path('inserts/', include('inserts.urls')),
    path('materials/', include('materials.urls')),
    path('rules/', include('rules.urls')),
    path('bulk-operations/', include('bulk_operations.urls')),
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('billing/', include('billing.urls')),
    
    # API endpoints
    path('api/v1/', include(api_patterns)),
    
    # API documentation
    path('docs/', include([
        path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
        path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
        path('swagger.json', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    ])),

    # Serve React app for all other routes
    re_path(r'^.*$', TemplateView.as_view(template_name='index.html')),
]

# Debug toolbar URLs (development only)
if settings.DEBUG:
    try:
        import debug_toolbar
        urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns
    except ImportError:
        pass
