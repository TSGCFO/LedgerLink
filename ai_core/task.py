# ai_core/tasks.py
from celery import shared_task
from django.conf import settings
from .feature_implementation.manager import FeatureManager
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def implement_feature_task(self, feature_request_id: int):
    """
    Celery task for implementing features asynchronously.
    """
    try:
        feature_manager = FeatureManager(settings.AI_SYSTEM_CONFIG)
        result = feature_manager.start_implementation(feature_request_id)
        logger.info(f"Feature implementation completed: {result}")
        return result
    except Exception as exc:
        logger.error(f"Feature implementation failed: {exc}")
        raise self.retry(exc=exc, countdown=300)  # Retry after 5 minutes