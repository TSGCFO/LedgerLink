"""
Tests for the Customer API endpoints.
"""

import pytest
from django.urls import reverse
from rest_framework import status

from .models import Customer
from test_utils.factories import CustomerFactory, UserFactory
from test_utils.mixins import APITestMixin

pytestmark = pytest.mark.django_db


class TestCustomerAPI(APITestMixin):
    """Tests for the Customer API endpoints."""

    def setUp(self):
        super().setUp()
        self.list_url = reverse('customer-list')
        self.customer = CustomerFactory(created_by=self.user)
        self.detail_url = reverse('customer-detail', kwargs={'pk': self.customer.pk})

    def test_list_customers(self):
        """Test retrieving a list of customers."""
        # Create additional customers
        CustomerFactory.create_batch(2, created_by=self.user)
        
        # Get all customers
        response = self.get_json_response(self.list_url)
        
        # Check response
        assert len(response['results']) == 3  # Including the one created in setUp
        assert response['count'] == 3

    def test_retrieve_customer(self):
        """Test retrieving a single customer."""
        response = self.get_json_response(self.detail_url)
        
        assert response['id'] == self.customer.pk
        assert response['company_name'] == self.customer.company_name
        assert response['contact_email'] == self.customer.contact_email

    def test_create_customer(self):
        """Test creating a new customer."""
        data = {
            'company_name': 'New Test Company',
            'contact_name': 'Jane Smith',
            'contact_email': 'jane@example.com',
            'contact_phone': '123-456-7890',
            'address': '123 Main St',
            'city': 'Anytown',
            'state': 'CA',
            'postal_code': '12345',
            'country': 'US'
        }
        
        response = self.get_json_response(
            self.list_url, 
            method='post', 
            data=data, 
            status_code=status.HTTP_201_CREATED
        )
        
        assert response['company_name'] == data['company_name']
        assert response['contact_email'] == data['contact_email']
        
        # Verify in database
        assert Customer.objects.filter(company_name=data['company_name']).exists()

    def test_update_customer(self):
        """Test updating an existing customer."""
        data = {
            'company_name': 'Updated Company Name',
            'contact_name': self.customer.contact_name,
            'contact_email': self.customer.contact_email
        }
        
        response = self.get_json_response(
            self.detail_url,
            method='patch',
            data=data,
            status_code=status.HTTP_200_OK
        )
        
        assert response['company_name'] == 'Updated Company Name'
        
        # Verify in database
        self.customer.refresh_from_db()
        assert self.customer.company_name == 'Updated Company Name'

    def test_delete_customer(self):
        """Test deleting a customer."""
        self.get_json_response(
            self.detail_url,
            method='delete',
            status_code=status.HTTP_204_NO_CONTENT
        )
        
        # Verify in database
        assert not Customer.objects.filter(pk=self.customer.pk).exists()

    def test_unauthenticated_access_denied(self):
        """Test that unauthenticated users cannot access the API."""
        # Create unauthenticated client
        self.client.force_authenticate(user=None)
        
        # Try to access list endpoint
        self.get_json_response(
            self.list_url,
            status_code=status.HTTP_401_UNAUTHORIZED
        )
        
        # Try to access detail endpoint
        self.get_json_response(
            self.detail_url,
            status_code=status.HTTP_401_UNAUTHORIZED
        )

    def test_unauthorized_user_cannot_modify_others_customers(self):
        """Test that users cannot modify customers created by other users."""
        # Create another user
        other_user = UserFactory()
        other_user_customer = CustomerFactory(created_by=other_user)
        other_detail_url = reverse('customer-detail', kwargs={'pk': other_user_customer.pk})
        
        # Try to update
        data = {'company_name': 'Should Not Update'}
        self.get_json_response(
            other_detail_url,
            method='patch',
            data=data,
            status_code=status.HTTP_403_FORBIDDEN
        )
        
        # Try to delete
        self.get_json_response(
            other_detail_url,
            method='delete',
            status_code=status.HTTP_403_FORBIDDEN
        )

    def test_invalid_data_returns_400(self):
        """Test that invalid data returns 400 Bad Request."""
        # Try to create with invalid email
        data = {
            'company_name': 'Test Company',
            'contact_name': 'Test Contact',
            'contact_email': 'not-an-email'  # Invalid email
        }
        
        self.get_json_response(
            self.list_url,
            method='post',
            data=data,
            status_code=status.HTTP_400_BAD_REQUEST
        )