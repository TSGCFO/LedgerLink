# Test Implementation Guide

This guide provides step-by-step instructions for implementing comprehensive tests for LedgerLink apps, following the patterns established for the materials app.

## Prerequisites

- Understand the Django testing framework
- Understand the app's models, serializers, and views
- Understand the testing patterns established in the billing app
- Review the existing tests for the app

## Step 1: Setup Test Directory Structure

Create the following directory structure for your app:

```
app_name/
├── tests/
│   ├── __init__.py
│   ├── factories.py
│   ├── test_models.py
│   ├── test_serializers.py
│   ├── test_views.py
│   ├── test_integration.py
│   ├── test_security.py
│   ├── test_pact_provider.py
│   └── test_performance.py
```

## Step 2: Implement Test Factories

Create factories for all models in the app:

```python
import factory
from factory.django import DjangoModelFactory
from decimal import Decimal
from app_name.models import Model1, Model2

class Model1Factory(DjangoModelFactory):
    """Factory for creating Model1 instances for testing."""
    
    class Meta:
        model = Model1
    
    # Define factory attributes for all fields
    field1 = factory.Sequence(lambda n: f'Field {n}')
    field2 = factory.Faker('paragraph', nb_sentences=3)
    # Use appropriate Faker providers for different field types

class Model2Factory(DjangoModelFactory):
    """Factory for creating Model2 instances for testing."""
    
    class Meta:
        model = Model2
    
    # Define factory attributes for all fields
    field1 = factory.Sequence(lambda n: f'Field {n}')
    # Include relationships to other models if needed
    related_model = factory.SubFactory(Model1Factory)
```

## Step 3: Implement Model Tests

Create comprehensive tests for all models:

```python
from django.test import TestCase
from django.db.utils import IntegrityError
from app_name.models import Model1, Model2
from app_name.tests.factories import Model1Factory, Model2Factory

class Model1Test(TestCase):
    """Test suite for the Model1 model."""

    def setUp(self):
        """Set up test data."""
        self.model1 = Model1Factory()

    def test_model_creation(self):
        """Test that a model instance can be created."""
        self.assertIsInstance(self.model1, Model1)
        # Test that all fields have the expected values

    def test_string_representation(self):
        """Test the string representation of the model."""
        self.assertEqual(str(self.model1), expected_string)

    def test_field_uniqueness(self):
        """Test that unique fields enforce uniqueness."""
        with self.assertRaises(IntegrityError):
            Model1Factory(unique_field=self.model1.unique_field)

    def test_field_validation(self):
        """Test field validation."""
        # Test validation for different fields

    def test_relationships(self):
        """Test model relationships."""
        # Test foreign keys, many-to-many relationships, etc.

    def test_edge_cases(self):
        """Test edge cases."""
        # Test with extreme values, empty values, etc.
```

## Step 4: Implement Serializer Tests

Create comprehensive tests for all serializers:

```python
from django.test import TestCase
from app_name.serializers import Model1Serializer, Model2Serializer
from app_name.tests.factories import Model1Factory, Model2Factory

class Model1SerializerTest(TestCase):
    """Test suite for the Model1Serializer."""

    def setUp(self):
        """Set up test data."""
        self.model1 = Model1Factory()
        self.serializer = Model1Serializer(instance=self.model1)

    def test_contains_expected_fields(self):
        """Test that the serializer contains the expected fields."""
        data = self.serializer.data
        expected_fields = ['id', 'field1', 'field2', ...]
        self.assertEqual(set(data.keys()), set(expected_fields))

    def test_field_content(self):
        """Test that fields contain the correct values."""
        data = self.serializer.data
        self.assertEqual(data['field1'], self.model1.field1)
        # Test other fields

    def test_validity_with_valid_data(self):
        """Test that the serializer is valid with valid data."""
        data = {
            'field1': 'Valid Value',
            'field2': 'Another Valid Value',
            # Include all required fields
        }
        serializer = Model1Serializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_invalidity_with_invalid_data(self):
        """Test that the serializer is invalid with invalid data."""
        data = {
            'field1': '',  # Empty value for required field
            'field2': 'Valid Value',
        }
        serializer = Model1Serializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('field1', serializer.errors)

    def test_create_model(self):
        """Test creating a new model using the serializer."""
        data = {
            'field1': 'New Value',
            'field2': 'Another New Value',
            # Include all required fields
        }
        serializer = Model1Serializer(data=data)
        self.assertTrue(serializer.is_valid())
        model = serializer.save()
        
        self.assertEqual(model.field1, 'New Value')
        # Test other fields
```

## Step 5: Implement View Tests

Create comprehensive tests for all views:

```python
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from app_name.models import Model1, Model2
from app_name.tests.factories import Model1Factory, Model2Factory

User = get_user_model()

class Model1ViewSetTest(APITestCase):
    """Test suite for the Model1ViewSet."""

    def setUp(self):
        """Set up test data."""
        self.model1 = Model1Factory()
        
        # Create a test user and authenticate
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        # URLs
        self.list_url = reverse('model1-list')
        self.detail_url = reverse('model1-detail', kwargs={'pk': self.model1.pk})

    def test_list_authenticated(self):
        """Test that authenticated users can list models."""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_list_unauthenticated(self):
        """Test that unauthenticated users cannot list models."""
        self.client.logout()
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve(self):
        """Test retrieving a single model."""
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.model1.id)
        # Test other fields

    def test_create(self):
        """Test creating a new model."""
        data = {
            'field1': 'New Value',
            'field2': 'Another New Value',
            # Include all required fields
        }
        
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['field1'], 'New Value')
        self.assertEqual(Model1.objects.count(), 2)

    def test_update(self):
        """Test updating a model."""
        data = {
            'field1': 'Updated Value',
            'field2': 'Another Updated Value',
            # Include all required fields
        }
        
        response = self.client.put(self.detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['field1'], 'Updated Value')
        
        # Verify the database was updated
        self.model1.refresh_from_db()
        self.assertEqual(self.model1.field1, 'Updated Value')

    def test_delete(self):
        """Test deleting a model."""
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Model1.objects.count(), 0)
```

## Step 6: Implement Integration Tests

Create tests that verify different components work together:

```python
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from app_name.models import Model1, Model2
from app_name.tests.factories import Model1Factory, Model2Factory

User = get_user_model()

class ModelIntegrationTest(TestCase):
    """Test the integration between Model1 and Model2 models and APIs."""

    def setUp(self):
        """Set up test data and client."""
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        # Create test instances of both models
        self.model1 = Model1Factory()
        self.model2 = Model2Factory()
    
    def test_multiple_api_calls(self):
        """Test making multiple API calls to retrieve models."""
        # Get model1 instances
        model1_response = self.client.get(reverse('model1-list'))
        self.assertEqual(model1_response.status_code, status.HTTP_200_OK)
        
        # Get model2 instances
        model2_response = self.client.get(reverse('model2-list'))
        self.assertEqual(model2_response.status_code, status.HTTP_200_OK)
        
        # Verify relationships between the models
    
    def test_concurrent_updates(self):
        """Test updating related models in sequence."""
        # Update model1
        model1_response = self.client.put(
            reverse('model1-detail', kwargs={'pk': self.model1.pk}),
            {'field1': 'Updated Value', 'field2': 'Another Updated Value'}
        )
        self.assertEqual(model1_response.status_code, status.HTTP_200_OK)
        
        # Update model2
        model2_response = self.client.put(
            reverse('model2-detail', kwargs={'pk': self.model2.pk}),
            {'field1': 'Updated Value', 'related_model': self.model1.pk}
        )
        self.assertEqual(model2_response.status_code, status.HTTP_200_OK)
        
        # Verify the updates worked
        self.model1.refresh_from_db()
        self.model2.refresh_from_db()
        self.assertEqual(self.model1.field1, 'Updated Value')
        # Verify relationships
```

## Step 7: Implement Security Tests

Create tests that verify security aspects:

```python
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from app_name.models import Model1, Model2
from app_name.tests.factories import Model1Factory, Model2Factory

User = get_user_model()

class ModelPermissionTest(TestCase):
    """Test permissions for Model API."""
    
    def setUp(self):
        """Set up test data."""
        # Create model instance
        self.model1 = Model1Factory()
        
        # Create user roles
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpass',
            is_staff=True
        )
        
        self.standard_user = User.objects.create_user(
            username='standard',
            email='standard@example.com',
            password='standardpass'
        )
        
        self.readonly_user = User.objects.create_user(
            username='readonly',
            email='readonly@example.com',
            password='readonlypass'
        )
        
        # Set up permissions
        model1_content_type = ContentType.objects.get_for_model(Model1)
        
        # Create a read-only group
        self.readonly_group = Group.objects.create(name='ReadOnly')
        view_model1_permission = Permission.objects.get(
            content_type=model1_content_type,
            codename='view_model1'
        )
        self.readonly_group.permissions.add(view_model1_permission)
        self.readonly_user.groups.add(self.readonly_group)
        
        # URLs
        self.list_url = reverse('model1-list')
        self.detail_url = reverse('model1-detail', kwargs={'pk': self.model1.pk})
        
        # API clients
        self.admin_client = APIClient()
        self.admin_client.force_authenticate(user=self.admin_user)
        
        self.standard_client = APIClient()
        self.standard_client.force_authenticate(user=self.standard_user)
        
        self.readonly_client = APIClient()
        self.readonly_client.force_authenticate(user=self.readonly_user)
        
        self.unauthenticated_client = APIClient()
    
    def test_unauthenticated_access(self):
        """Test that unauthenticated users cannot access the API."""
        response = self.unauthenticated_client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_readonly_user_permissions(self):
        """Test that readonly users can only view models."""
        # Should be able to view models
        response = self.readonly_client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Should not be able to create models
        response = self.readonly_client.post(self.list_url, {
            'field1': 'New Value',
            'field2': 'Another New Value'
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Should not be able to update models
        response = self.readonly_client.put(self.detail_url, {
            'field1': 'Updated Value',
            'field2': 'Another Updated Value'
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
```

## Step 8: Implement Contract Tests

Create tests that verify API contracts:

```python
import os
import json
import logging
from pact import Verifier
from django.test import TestCase
from django.conf import settings
from app_name.models import Model1, Model2
from app_name.tests.factories import Model1Factory, Model2Factory

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Model1PactProviderTest(TestCase):
    """
    Test that the Model1 API can satisfy the contract
    defined by the frontend consumer.
    """
    
    def setUp(self):
        """Set up test data and pact verifier."""
        # Create test instances
        self.model1 = Model1Factory(id=1)  # Explicitly set ID for deterministic tests
        
        # Pact setup
        self.pact_dir = os.path.join(settings.BASE_DIR, 'frontend', 'pact', 'pacts')
        self.pact_uri = f"http://{settings.ALLOWED_HOSTS[0] if settings.ALLOWED_HOSTS else 'localhost'}:8000"
        self.provider_name = 'ledgerlink-model1-provider'
        self.consumer_name = 'ledgerlink-model1-consumer'
        
        # Verifier setup
        self.verifier = Verifier(
            provider="ledgerlink-model1-provider",
            provider_base_url=self.pact_uri
        )
    
    def test_model1_contract(self):
        """Test that the API satisfies the model1 contract."""
        pact_file = os.path.join(self.pact_dir, f"{self.consumer_name}-{self.provider_name}.json")
        
        # Check if pact file exists
        if not os.path.exists(pact_file):
            logger.warning(f"Pact file {pact_file} does not exist. Skipping test.")
            return
        
        # Define state handlers for provider states
        provider_states = {
            "models exist": self._models_exist,
            "no models exist": self._no_models_exist,
            "a specific model exists": self._specific_model_exists
        }
        
        # Verify the contract
        success, logs = self.verifier.verify_pacts(
            pact_files=[pact_file],
            provider_states_setup_url=f"{self.pact_uri}/pact-provider-state",
            provider_states=provider_states,
            verbose=True
        )
        
        # Log results
        for log in logs:
            logger.info(log)
        
        # Assert that verification was successful
        self.assertTrue(success)
    
    def _models_exist(self, provider_state):
        """Set up state where models exist."""
        # Models are already created in setUp
        return True
    
    def _no_models_exist(self, provider_state):
        """Set up state where no models exist."""
        Model1.objects.all().delete()
        return True
    
    def _specific_model_exists(self, provider_state):
        """Set up state where a specific model exists."""
        # Recreate model with id=1 if it doesn't exist
        Model1.objects.filter(id=1).delete()
        Model1Factory(
            id=1,
            field1='Specific Value',
            field2='Another Specific Value'
        )
        return True
```

## Step 9: Implement Performance Tests

Create tests that verify API performance:

```python
import time
import random
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.db import connection, reset_queries
from django.test.utils import CaptureQueriesContext
from rest_framework.test import APIClient
from app_name.models import Model1, Model2
from app_name.tests.factories import Model1Factory, Model2Factory

User = get_user_model()

class ModelQueryPerformanceTest(TestCase):
    """Test database query performance for Model1 model."""
    
    def setUp(self):
        """Set up test data for performance testing."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        # Create a large number of models for performance testing
        self.model_count = 50
        for i in range(self.model_count):
            Model1Factory()
    
    def test_query_count_list(self):
        """Test the number of queries executed for listing models."""
        url = reverse('model1-list')
        
        with CaptureQueriesContext(connection) as queries:
            response = self.client.get(url)
            
        # Verify the response
        self.assertEqual(response.status_code, 200)
        
        # Check query count - should be a small number regardless of model count
        query_count = len(queries)
        self.assertLessEqual(query_count, 5, 
                            f"Too many queries ({query_count}) for model list endpoint")
    
    def test_query_execution_time(self):
        """Test the execution time for retrieving a list of models."""
        url = reverse('model1-list')
        
        # Measure execution time
        start_time = time.time()
        response = self.client.get(url)
        end_time = time.time()
        
        # Verify the response
        self.assertEqual(response.status_code, 200)
        
        # Calculate execution time in milliseconds
        execution_time = (end_time - start_time) * 1000  # Convert to milliseconds
        
        # Execution time should be reasonable
        self.assertLess(execution_time, 500, 
                       f"API response too slow: {execution_time:.2f}ms")
```

## Step 10: Run and Verify Tests

Run the tests and verify that they pass:

```bash
python manage.py test app_name
```

## Step 11: Check Test Coverage

Use coverage to check test coverage:

```bash
coverage run --source='app_name' manage.py test app_name
coverage report
coverage html
```

Aim for 90%+ coverage for the app.

## Step 12: Document Tests

Document the tests in a README.md file in the tests directory:

```markdown
# App Name Tests

This directory contains tests for the App Name app. The tests are organized as follows:

## Test Files

- `factories.py`: Factories for creating test instances
- `test_models.py`: Tests for models
- `test_serializers.py`: Tests for serializers
- `test_views.py`: Tests for views/API endpoints
- `test_integration.py`: Tests for components working together
- `test_security.py`: Tests for security and permissions
- `test_pact_provider.py`: Tests for API contracts
- `test_performance.py`: Tests for API performance

## Running Tests

To run all tests for this app:

```bash
python manage.py test app_name
```

To run a specific test file:

```bash
python manage.py test app_name.tests.test_models
```

To run a specific test class:

```bash
python manage.py test app_name.tests.test_models.Model1Test
```

To run a specific test method:

```bash
python manage.py test app_name.tests.test_models.Model1Test.test_model_creation
```

## Test Coverage

This app has [90+%] test coverage. To check test coverage:

```bash
coverage run --source='app_name' manage.py test app_name
coverage report
```
```