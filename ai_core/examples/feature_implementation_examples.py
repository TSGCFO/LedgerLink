# ai_core/examples/feature_implementation_examples.py
from ..models import FeatureRequest
from ..feature_implementation import FeatureImplementer, FeatureManager
from django.contrib.auth import get_user_model
from ..feature_implementation.implementer import FeatureImplementer
from ..feature_implementation.manager import FeatureManager


def feature_implementation_example(user_id: int):
    """
    Example of implementing a feature
    """
    # Create feature request
    user = get_user_model().objects.get(id=user_id)
    feature_request = FeatureRequest.objects.create(
        title='Add product search functionality',
        description='Implement a search feature to allow users to search for products by name or description.',
        requested_by=user
    )

    # Implement feature
    implementer = FeatureImplementer()
    result = implementer.implement_feature(feature_request.id)

    return result


def feature_management_example(user_id: int):
    """
    Example of managing feature implementations
    """
    manager = FeatureManager()

    # Create feature request
    feature_request = manager.create_feature_request(
        title='Add export functionality',
        description='Add ability to export data to CSV and PDF formats',
        user_id=user_id
    )

    # Start implementation
    implementation_result = manager.start_implementation(feature_request.id)

    # Get status
    status = manager.get_implementation_status(feature_request.id)

    return {
        'feature_request': feature_request,
        'implementation_result': implementation_result,
        'status': status
    }