# ai_core/middleware.py
from django.conf import settings
from .models import AIOperation
import time


class AIMonitoringMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not settings.AI_SYSTEM_CONFIG['enabled']:
            return self.get_response(request)

        start_time = time.time()

        response = self.get_response(request)

        # Record operation metrics
        duration = time.time() - start_time

        if hasattr(request, 'ai_operation_id'):
            AIOperation.objects.filter(id=request.ai_operation_id).update(
                details__response_time=duration,
                details__status_code=response.status_code
            )

        return response