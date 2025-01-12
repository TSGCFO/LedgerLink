# ai_core/feature_implementation/manager.py
from typing import Dict, Any, Optional
from django.db import transaction
from django.core.exceptions import ValidationError
from ..models import FeatureRequest, AIOperation
from ..components import BaseComponent, ComponentConfig
from .implementer import FeatureImplementer


class FeatureManager(BaseComponent):
    """
    Manages feature implementation workflow and coordination.
    """

    def __init__(self, config: ComponentConfig):
        super().__init__(config)
        self.implementer = None
        self.max_concurrent = config.settings.get('max_concurrent_implementations', 3)

    def _setup(self):
        """Initialize the feature manager"""
        self.implementer = FeatureImplementer(self.config)

    def create_feature_request(self, title: str, description: str, user=None) -> FeatureRequest:
        """
        Creates a new feature request.

        Args:
            title: Feature request title
            description: Detailed description of the feature
            user: User requesting the feature

        Returns:
            Created FeatureRequest instance
        """
        try:
            feature_request = FeatureRequest.objects.create(
                title=title,
                description=description,
                requested_by=user
            )
            return feature_request
        except Exception as e:
            raise ValidationError(f"Failed to create feature request: {str(e)}")

    def start_implementation(self, feature_request_id: int) -> Dict[str, Any]:
        """
        Starts the implementation process for a feature request.

        Args:
            feature_request_id: ID of the feature request to implement

        Returns:
            Dictionary containing implementation status and details
        """
        # Check concurrent implementations
        active_count = FeatureRequest.objects.filter(
            status__in=['implementing', 'testing']
        ).count()

        if active_count >= self.max_concurrent:
            raise ValidationError(
                f"Maximum concurrent implementations ({self.max_concurrent}) reached"
            )

        return self.implementer.implement_feature(feature_request_id)

    def get_implementation_status(self, feature_request_id: int) -> Dict[str, Any]:
        """
        Gets the current status of a feature implementation.

        Args:
            feature_request_id: ID of the feature request

        Returns:
            Dictionary containing status information
        """
        try:
            feature_request = FeatureRequest.objects.get(id=feature_request_id)
            return {
                'status': feature_request.status,
                'analysis_result': feature_request.analysis_result,
                'implementation_details': feature_request.implementation_details,
                'operations': self._get_feature_operations(feature_request_id)
            }
        except FeatureRequest.DoesNotExist:
            raise ValidationError(f"Feature request {feature_request_id} not found")

    def cancel_implementation(self, feature_request_id: int) -> Dict[str, str]:
        """
        Cancels an ongoing feature implementation.

        Args:
            feature_request_id: ID of the feature request to cancel

        Returns:
            Dictionary containing cancellation status
        """
        try:
            with transaction.atomic():
                feature_request = FeatureRequest.objects.select_for_update().get(
                    id=feature_request_id
                )

                if feature_request.status not in ['implementing', 'testing']:
                    raise ValidationError(
                        f"Cannot cancel feature in {feature_request.status} status"
                    )

                feature_request.status = 'failed'
                feature_request.save()

                # Mark related operations as failed
                AIOperation.objects.filter(
                    details__feature_request_id=feature_request_id,
                    status__in=['pending', 'in_progress']
                ).update(
                    status='failed',
                    error_message='Implementation cancelled by user'
                )

                return {
                    'status': 'cancelled',
                    'message': 'Feature implementation cancelled successfully'
                }

        except FeatureRequest.DoesNotExist:
            raise ValidationError(f"Feature request {feature_request_id} not found")

    def _get_feature_operations(self, feature_request_id: int) -> Dict[str, Any]:
        """
        Gets all operations related to a feature request.

        Args:
            feature_request_id: ID of the feature request

        Returns:
            Dictionary containing operation details
        """
        operations = AIOperation.objects.filter(
            details__feature_request_id=feature_request_id
        ).order_by('-started_at')

        return {
            'total': operations.count(),
            'completed': operations.filter(status='completed').count(),
            'failed': operations.filter(status='failed').count(),
            'in_progress': operations.filter(status='in_progress').count(),
            'latest_operation': self._get_latest_operation(operations)
        }

    def _get_latest_operation(self, operations) -> Optional[Dict[str, Any]]:
        """
        Gets details of the most recent operation.

        Args:
            operations: QuerySet of operations

        Returns:
            Dictionary containing latest operation details or None
        """
        latest = operations.first()
        if latest:
            return {
                'type': latest.operation_type,
                'status': latest.status,
                'started_at': latest.started_at,
                'completed_at': latest.completed_at,
                'error_message': latest.error_message
            }
        return None