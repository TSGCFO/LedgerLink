from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def api_root(request, format=None):
    """
    API root view that provides links to available endpoints.
    """
    return Response({
        'status': 'ok',
        'message': 'LedgerLink API v1',
        'endpoints': {
            'customers': '/api/v1/customers/',
            'customer_services': '/api/v1/customer-services/',
            'orders': '/api/v1/orders/',
            'products': '/api/v1/products/',
            'billing': '/api/v1/billing/',
            'services': '/api/v1/services/',
            'shipping': {
                'cad': '/api/v1/shipping/cad/',
                'us': '/api/v1/shipping/us/'
            },
            'inserts': '/api/v1/inserts/',
            'materials': '/api/v1/materials/',
            'rules': '/api/v1/rules/',
            'bulk_operations': '/api/v1/bulk-operations/',
            'auth': {
                'token': '/api/v1/auth/token/',
                'refresh': '/api/v1/auth/token/refresh/',
                'verify': '/api/v1/auth/token/verify/'
            },
            'docs': '/docs/swagger/'
        }
    })
