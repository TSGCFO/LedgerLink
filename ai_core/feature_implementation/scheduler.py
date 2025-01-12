# ai_core/feature_implementation/scheduler.py
from typing import List, Dict, Any
from django.utils import timezone
from datetime import timedelta
from ..models import FeatureRequest
from .manager import FeatureManager


class FeatureScheduler:
    """
    Schedules and prioritizes feature implementations.
    """

    def __init__(self, feature_manager: FeatureManager):
        self.feature_manager = feature_manager

    def get_next_features(self, limit: int = 5) -> List[FeatureRequest]:
        """
        Gets the next features to implement based on priority.

        Args:
            limit: Maximum number of features to return

        Returns:
            List of FeatureRequest instances
        """
        return FeatureRequest.objects.filter(
            status='pending'
        ).order_by(
            'created_at'
        )[:limit]

    def schedule_implementation(self, feature_request_id: int, priority: str = 'normal') -> Dict[str, Any]:
        """
        Schedules a feature for implementation.

        Args:
            feature_request_id: ID of the feature request
            priority: Priority level ('high', 'normal', 'low')

        Returns:
            Dictionary containing scheduling details
        """
        try:
            feature_request = FeatureRequest.objects.get(id=feature_request_id)

            if feature_request.status != 'pending':
                raise ValueError(
                    f"Cannot schedule feature in {feature_request.status} status"
                )

            # Check resource availability
            if self._can_start_implementation():
                return self.feature_manager.start_implementation(feature_request_id)
            else:
                return {
                    'status': 'scheduled',
                    'message': 'Feature implementation scheduled for later',
                    'estimated_start': self._estimate_start_time()
                }

        except FeatureRequest.DoesNotExist:
            raise ValueError(f"Feature request {feature_request_id} not found")

    def _can_start_implementation(self) -> bool:
        """
        Checks if a new implementation can be started.

        Returns:
            Boolean indicating if implementation can start
        """
        active_count = FeatureRequest.objects.filter(
            status__in=['implementing', 'testing']
        ).count()

        return active_count < self.feature_manager.max_concurrent

    def _estimate_start_time(self) -> timezone.datetime:
        """
        Estimates when the next implementation can start.

        Returns:
            Estimated datetime
        """
        active_implementations = FeatureRequest.objects.filter(
            status__in=['implementing', 'testing']
        ).order_by('updated_at')

        if not active_implementations:
            return timezone.now()

        # Estimate based on average implementation time
        avg_implementation_time = timedelta(hours=2)  # Default estimate
        return active_implementations.first().updated_at + avg_implementation_time