"""
Tests for Orders views.
"""

import pytest
from django.urls import reverse
from django.contrib.messages import get_messages

from orders.models import Order
from test_utils.factories import OrderFactory, CustomerFactory, UserFactory
from test_utils.mixins import ViewTestMixin

pytestmark = pytest.mark.django_db


class TestOrderViews(ViewTestMixin):
    """Tests for the Order views."""

    def setUp(self):
        super().setUp()
        self.customer = CustomerFactory(created_by=self.user)
        self.order = OrderFactory(customer=self.customer, created_by=self.user)
        self.list_url = self.get_url('order-list')
        self.detail_url = self.get_url('order-detail', kwargs={'pk': self.order.pk})
        self.create_url = self.get_url('order-create')
        self.update_url = self.get_url('order-update', kwargs={'pk': self.order.pk})
        self.delete_url = self.get_url('order-delete', kwargs={'pk': self.order.pk})

    def test_order_list_view(self):
        """Test the order list view."""
        # Create additional orders
        OrderFactory.create_batch(2, customer=self.customer, created_by=self.user)
        
        response = self.get_response(self.list_url)
        
        assert response.status_code == 200
        assert 'orders' in response.context
        assert len(response.context['orders']) == 3  # Including the one created in setUp

    def test_order_detail_view(self):
        """Test the order detail view."""
        response = self.get_response(self.detail_url)
        
        assert response.status_code == 200
        assert 'order' in response.context
        assert response.context['order'].pk == self.order.pk

    def test_order_create_view_get(self):
        """Test the GET request to the order create view."""
        response = self.get_response(self.create_url)
        
        assert response.status_code == 200
        assert 'form' in response.context
        assert 'customers' in response.context

    def test_order_create_view_post(self):
        """Test creating an order via POST request."""
        data = {
            'customer': self.customer.pk,
            'order_number': 'ORD-TEST-123',
            'order_date': '2025-03-03',
            'status': 'pending',
            'shipping_address': '123 Ship St',
            'shipping_city': 'Shiptown',
            'shipping_state': 'ST',
            'shipping_postal_code': '12345',
            'shipping_country': 'US'
        }
        
        response = self.get_response(self.create_url, method='post', data=data, follow=True)
        
        assert response.status_code == 200
        # Check for success message
        messages = list(get_messages(response.wsgi_request))
        assert any('successfully created' in str(m) for m in messages)
        
        # Verify in database
        assert Order.objects.filter(order_number='ORD-TEST-123').exists()

    def test_order_update_view_get(self):
        """Test the GET request to the order update view."""
        response = self.get_response(self.update_url)
        
        assert response.status_code == 200
        assert 'form' in response.context
        assert 'order' in response.context
        assert response.context['order'].pk == self.order.pk

    def test_order_update_view_post(self):
        """Test updating an order via POST request."""
        data = {
            'customer': self.customer.pk,
            'order_number': self.order.order_number,
            'order_date': '2025-03-03',
            'status': 'shipped',  # Updated status
            'shipping_address': self.order.shipping_address,
            'shipping_city': self.order.shipping_city,
            'shipping_state': self.order.shipping_state,
            'shipping_postal_code': self.order.shipping_postal_code,
            'shipping_country': self.order.shipping_country
        }
        
        response = self.get_response(self.update_url, method='post', data=data, follow=True)
        
        assert response.status_code == 200
        # Check for success message
        messages = list(get_messages(response.wsgi_request))
        assert any('successfully updated' in str(m) for m in messages)
        
        # Verify in database
        self.order.refresh_from_db()
        assert self.order.status == 'shipped'

    def test_order_delete_view_get(self):
        """Test the GET request to the order delete view."""
        response = self.get_response(self.delete_url)
        
        assert response.status_code == 200
        assert 'order' in response.context
        assert response.context['order'].pk == self.order.pk

    def test_order_delete_view_post(self):
        """Test deleting an order via POST request."""
        response = self.get_response(self.delete_url, method='post', follow=True)
        
        assert response.status_code == 200
        # Check for success message
        messages = list(get_messages(response.wsgi_request))
        assert any('successfully deleted' in str(m) for m in messages)
        
        # Verify in database
        assert not Order.objects.filter(pk=self.order.pk).exists()

    def test_unauthenticated_user_redirected_to_login(self):
        """Test that unauthenticated users are redirected to login."""
        # Log out client
        self.client.logout()
        
        # Try to access list view
        response = self.get_response(self.list_url)
        
        # Should redirect to login
        assert response.status_code == 302
        assert 'login' in response['Location']

    def test_unauthorized_user_cannot_access_others_orders(self):
        """Test that users cannot access orders created by other users."""
        # Create another user and their order
        other_user = UserFactory()
        other_customer = CustomerFactory(created_by=other_user)
        other_order = OrderFactory(customer=other_customer, created_by=other_user)
        other_detail_url = self.get_url('order-detail', kwargs={'pk': other_order.pk})
        
        # Try to access the other user's order
        response = self.get_response(other_detail_url)
        
        # Should return 403 Forbidden
        assert response.status_code == 403