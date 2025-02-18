from django.urls import path, include
from rest_framework.routers import DefaultRouter
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.conf import settings
from rest_framework import permissions
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

# Initialize API router
router = DefaultRouter()

# Schema view for API documentation
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
urlpatterns = [
    # API documentation
    path('docs/', include([
        path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
        path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
        path('swagger.json', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    ])),

    # API versioning
    path('v1/', include([
        # Authentication endpoints
        path('auth/', include([
            path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
            path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
            path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
        ])),

        # Include router URLs
        path('', include(router.urls)),
        
        # Include app-specific URLs
        path('customers/', include('api.v1.customers.urls')),
        path('orders/', include('api.v1.orders.urls')),
        path('products/', include('api.v1.products.urls')),
        path('billing/', include('api.v1.billing.urls')),
        path('services/', include('api.v1.services.urls')),
        path('shipping/', include('api.v1.shipping.urls')),

        # Add bulk operations URLs
        path('bulk-operations/', include('bulk_operations.urls')),
    ])),
]

# Debug toolbar URLs (development only)
if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns

# API version configuration
API_VERSIONS = {
    'v1': {
        'active': True,
        'end_of_life': None,
        'deprecated': False,
    }
}

# Custom 404 and 500 handlers
handler404 = 'api.views.error_views.custom_404'
handler500 = 'api.views.error_views.custom_500'