# ai_core/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import FeatureRequest, AIOperation
import logging

logger = logging.getLogger(__name__)

try:
    from .tasks import implement_feature_task
except ImportError:
    logger.warning("Celery tasks not available. Feature implementation will be synchronous.")
    implement_feature_task = None

@receiver(post_save, sender=FeatureRequest)
def handle_feature_request_save(sender, instance, created, **kwargs):
    """
    Handles feature request creation and status changes.
    """
    if created:
        logger.info(f"New feature request created: {instance.id}")
        if implement_feature_task:
            implement_feature_task.delay(instance.id)
    else:
        logger.info(f"Feature request {instance.id} status changed to: {instance.status}")

@receiver(post_save, sender=AIOperation)
def handle_operation_save(sender, instance, created, **kwargs):
    """
    Handles AI operation status changes.
    """
    if created:
        logger.info(f"New AI operation started: {instance.operation_type}")
    elif instance.status in ['completed', 'failed']:
        logger.info(
            f"AI operation {instance.id} {instance.status}: {instance.error_message}"
        )