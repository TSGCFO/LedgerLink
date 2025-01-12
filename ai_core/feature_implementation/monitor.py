# ai_core/feature_implementation/monitor.py
from typing import Dict, Any, List
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
from ..models import FeatureRequest, AIOperation


class ImplementationMonitor:
    """
    Monitors and reports on feature implementations.
    """

    def get_implementation_stats(self) -> Dict[str, Any]:
        """
        Gets overall implementation statistics.

        Returns:
            Dictionary containing implementation statistics
        """
        return {
            'total_requests': FeatureRequest.objects.count(),
            'completed': FeatureRequest.objects.filter(status='completed').count(),
            'failed': FeatureRequest.objects.filter(status='failed').count(),
            'in_progress': FeatureRequest.objects.filter(
                status__in=['implementing', 'testing']
            ).count(),
            'success_rate': self._calculate_success_rate(),
            'avg_implementation_time': self._calculate_avg_implementation_time()
        }

    def get_active_implementations(self) -> List[Dict[str, Any]]:
        """
        Gets details of all active implementations.

        Returns:
            List of dictionaries containing implementation details
        """
        active_features = FeatureRequest.objects.filter(
            status__in=['implementing', 'testing']
        ).select_related('requested_by')

        return [{
            'id': feature.id,
            'title': feature.title,
            'status': feature.status,
            'requested_by': feature.requested_by.username if feature.requested_by else None,
            'started_at': feature.updated_at,
            'duration': timezone.now() - feature.updated_at
        } for feature in active_features]

    def get_failed_implementations(self, days: int = 7) -> List[Dict[str, Any]]:
        """
        Gets details of failed implementations.

        Args:
            days: Number of days to look back

        Returns:
            List of dictionaries containing failure details
        """
        since = timezone.now() - timedelta(days=days)

        failed_features = FeatureRequest.objects.filter(
            status='failed',
            updated_at__gte=since
        ).select_related('requested_by')

        return [{
            'id': feature.id,
            'title': feature.title,
            'requested_by': feature.requested_by.username if feature.requested_by else None,
            'failed_at': feature.updated_at,
            'error_details': self._get_failure_details(feature.id)
        } for feature in failed_features]

    def _calculate_success_rate(self) -> float:
        """
        Calculates the implementation success rate.

        Returns:
            Success rate as a percentage
        """
        total = FeatureRequest.objects.filter(
            status__in=['completed', 'failed']
        ).count()

        if total == 0:
            return 0.0

        completed = FeatureRequest.objects.filter(status='completed').count()
        return (completed / total) * 100

    def _calculate_avg_implementation_time(self) -> timedelta:
        """
        Calculates average implementation time.

        Returns:
            Average implementation time as timedelta
        """
        completed_features = FeatureRequest.objects.filter(
            status='completed'
        )

        if not completed_features:
            return timedelta(0)

        total_time = timedelta(0)
        count = 0

        for feature in completed_features:
            implementation_time = self._get_implementation_time(feature)
            if implementation_time:
                total_time += implementation_time
                count += 1

        return total_time / count if count > 0 else timedelta(0)

    def _get_implementation_time(self, feature: FeatureRequest) -> timedelta:
        """
        Calculates implementation time for a feature.

        Args:
            feature: FeatureRequest instance

        Returns:
            Implementation time as timedelta
        """
        start_operation = AIOperation.objects.filter(
            details__feature_request_id=feature.id,
            operation_type='feature'
        ).order_by('started_at').first()

        if not start_operation:
            return None

        return feature.updated_at - start_operation.started_at

    def _get_failure_details(self, feature_id: int) -> Dict[str, Any]:
        """
        Gets detailed information about a failed implementation.

        Args:
            feature_id: ID of the failed feature request

        Returns:
            Dictionary containing failure details
        """
        failed_operation = AIOperation.objects.filter(
            details__feature_request_id=feature_id,
            status='failed'
        ).order_by('-started_at').first()

        if failed_operation:
            return {
                'operation_type': failed_operation.operation_type,
                'error_message': failed_operation.error_message,
                'failed_at': failed_operation.completed_at or failed_operation.started_at
            }
        return None