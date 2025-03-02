"""
API views for client-side logging
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from ..utils.logging_utils import (
    save_client_logs,
    list_client_log_files,
    get_client_log_file_content
)
from ..middleware import get_client_ip

@api_view(['POST'])
def save_client_logs(request):
    """
    Save client logs to a file on the server
    """
    logs = request.data.get('logs', [])
    
    if not logs:
        return Response(
            {'error': 'No logs provided'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Get user info for the log file
    user_info = None
    if request.user.is_authenticated:
        user_info = {
            'id': request.user.id,
            'username': request.user.username,
            'email': request.user.email,
        }
    
    # Add client info to the metadata
    client_info = {
        'ip': get_client_ip(request),
        'user_agent': request.META.get('HTTP_USER_AGENT', 'Unknown'),
    }
    
    # Save logs to a file
    result = save_client_logs(logs, {
        'user': user_info,
        'client': client_info,
    })
    
    if result.get('success'):
        return Response(result, status=status.HTTP_201_CREATED)
    else:
        return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_client_logs(request):
    """
    List all client log files (admin only)
    """
    if not request.user.is_staff:
        return Response(
            {'error': 'Permission denied'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    files = list_client_log_files()
    return Response({'files': files})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_client_log_file(request, filename):
    """
    Get the content of a client log file (admin only)
    """
    if not request.user.is_staff:
        return Response(
            {'error': 'Permission denied'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    result = get_client_log_file_content(filename)
    
    if result.get('success'):
        return Response(result)
    else:
        return Response(result, status=status.HTTP_404_NOT_FOUND)