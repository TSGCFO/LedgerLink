import json
import logging
import os
import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from orders.models import Order
from orders.tests.factories import OrderFactory, SubmittedOrderFactory, ShippedOrderFactory
from customers.tests.factories import CustomerFactory

# Try to import pact libraries, but don't fail if not available
try:
    from pact import Verifier
    HAS_PACT = True
except (ImportError, ModuleNotFoundError):
    HAS_PACT = False

logger = logging.getLogger(__name__)

# Paths and configuration for PACT
PACT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'frontend', 'pact')
PACT_FILE = os.path.join(PACT_DIR, 'pacts', 'react-app-order-api.json')
PACT_BROKER_URL = os.environ.get('PACT_BROKER_URL', 'http://localhost:9292')
PROVIDER_NAME = 'order-api'
PROVIDER_URL = os.environ.get('PROVIDER_URL', 'http://localhost:8000')


@pytest.mark.skipif(not HAS_PACT, reason="Pact library not available")
@pytest.mark.pact
class TestOrderPactProvider:
    """Test the order API as a PACT provider."""
    
    @classmethod
    def setup_class(cls):
        """Set up the test class."""
        # Set up API client
        cls.client = APIClient()
        # Authenticate the client (if needed)
        from api.tests.factories import UserFactory
        user = UserFactory(is_staff=True)
        cls.client.force_authenticate(user=user)
        
    def setup_method(self, method):
        """Set up for each test method."""
        # Create test data
        self.customer = CustomerFactory(
            company_name="Test Company",
            email="test@example.com"
        )
        self.order = OrderFactory(
            customer=self.customer,
            reference_number="REF-001",
            status="draft",
            priority="medium",
            sku_quantity={"SKU-001": 10, "SKU-002": 5}
        )
        
    def teardown_method(self, method):
        """Clean up after each test method."""
        # Clean up test data
        Order.objects.all().delete()
    
    def test_get_order_list(self):
        """Test GET request to order list endpoint."""
        # Set up test data
        orders = [OrderFactory(customer=self.customer) for _ in range(5)]
        
        # Make the request
        url = reverse('order-list')
        response = self.client.get(url)
        
        # Verify the response
        assert response.status_code == 200
        assert response.data['success'] is True
        
        # The response data should include all orders
        order_ids = [order.transaction_id for order in orders]
        for item in response.data['data']:
            assert item['transaction_id'] in order_ids + [self.order.transaction_id]
    
    def test_get_order_by_id(self):
        """Test GET request to order detail endpoint."""
        # Make the request
        url = reverse('order-detail', kwargs={'pk': self.order.transaction_id})
        response = self.client.get(url)
        
        # Verify the response
        assert response.status_code == 200
        assert response.data['transaction_id'] == self.order.transaction_id
        assert response.data['reference_number'] == self.order.reference_number
        assert response.data['customer'] == self.customer.id
        assert response.data['customer_details']['company_name'] == self.customer.company_name
    
    def test_get_orders_by_customer(self):
        """Test GET request to filter orders by customer."""
        # Create orders for different customers
        other_customer = CustomerFactory()
        OrderFactory(customer=other_customer)
        OrderFactory(customer=other_customer)
        customer_orders = [
            OrderFactory(customer=self.customer),
            OrderFactory(customer=self.customer)
        ]
        
        # Make the request
        url = f"{reverse('order-list')}?customer={self.customer.id}"
        response = self.client.get(url)
        
        # Verify the response
        assert response.status_code == 200
        assert response.data['success'] is True
        
        # Should only include orders for the requested customer
        response_orders = response.data['data']
        order_ids = [o['transaction_id'] for o in response_orders]
        
        for order in customer_orders:
            assert order.transaction_id in order_ids
        
        # Verify order count is correct (including the self.order created in setup)
        assert len(response_orders) == len(customer_orders) + 1
    
    def test_create_order(self):
        """Test POST request to create an order."""
        # Prepare data for creating a new order
        new_order_data = {
            'customer': self.customer.id,
            'reference_number': 'REF-002',
            'status': 'draft',
            'priority': 'high',
            'ship_to_name': 'Test Recipient',
            'ship_to_address': '123 Test St',
            'ship_to_city': 'Test City',
            'ship_to_state': 'TS',
            'ship_to_zip': '12345',
            'sku_quantity': {"SKU-003": 3, "SKU-004": 7}
        }
        
        # Make the request
        url = reverse('order-list')
        response = self.client.post(url, new_order_data, format='json')
        
        # Verify the response
        assert response.status_code == 201
        assert response.data['success'] is True
        assert response.data['data']['reference_number'] == 'REF-002'
        assert response.data['data']['customer'] == self.customer.id
        assert response.data['data']['status'] == 'draft'
        assert response.data['data']['priority'] == 'high'
        
        # Verify the order was created in the database
        assert Order.objects.filter(reference_number='REF-002').exists()
    
    def test_update_order(self):
        """Test PUT request to update an order."""
        # Prepare data for updating the order
        update_data = {
            'customer': self.customer.id,
            'reference_number': 'REF-001-UPDATED',
            'status': 'submitted',  # Update status
            'priority': 'high',     # Update priority
            'ship_to_name': 'Updated Recipient',
            'ship_to_address': '456 Update St',
            'ship_to_city': 'Update City',
            'ship_to_state': 'US',
            'ship_to_zip': '54321',
            'sku_quantity': self.order.sku_quantity
        }
        
        # Make the request
        url = reverse('order-detail', kwargs={'pk': self.order.transaction_id})
        response = self.client.put(url, update_data, format='json')
        
        # Verify the response
        assert response.status_code == 200
        assert response.data['success'] is True
        assert response.data['data']['reference_number'] == 'REF-001-UPDATED'
        assert response.data['data']['status'] == 'submitted'
        assert response.data['data']['priority'] == 'high'
        
        # Verify the order was updated in the database
        self.order.refresh_from_db()
        assert self.order.reference_number == 'REF-001-UPDATED'
        assert self.order.status == 'submitted'
        assert self.order.priority == 'high'
    
    def test_patch_order(self):
        """Test PATCH request to partially update an order."""
        # Prepare data for partially updating the order
        patch_data = {
            'priority': 'high'
        }
        
        # Make the request
        url = reverse('order-detail', kwargs={'pk': self.order.transaction_id})
        response = self.client.patch(url, patch_data, format='json')
        
        # Verify the response
        assert response.status_code == 200
        assert response.data['success'] is True
        assert response.data['data']['priority'] == 'high'
        
        # Verify the order was updated in the database
        self.order.refresh_from_db()
        assert self.order.priority == 'high'
    
    def test_cancel_order(self):
        """Test POST request to cancel an order."""
        # Make the request
        url = reverse('order-cancel', kwargs={'pk': self.order.transaction_id})
        response = self.client.post(url)
        
        # Verify the response
        assert response.status_code == 200
        assert response.data['success'] is True
        assert 'Order cancelled successfully' in response.data['message']
        assert response.data['data']['status'] == 'cancelled'
        
        # Verify the order was cancelled in the database
        self.order.refresh_from_db()
        assert self.order.status == 'cancelled'
    
    def test_delete_order(self):
        """Test DELETE request to delete an order."""
        # Create a draft order to delete
        order_to_delete = OrderFactory(customer=self.customer, status='draft')
        
        # Make the request
        url = reverse('order-detail', kwargs={'pk': order_to_delete.transaction_id})
        response = self.client.delete(url)
        
        # Verify the response
        assert response.status_code == 200
        assert response.data['success'] is True
        assert 'Order deleted successfully' in response.data['message']
        
        # Verify the order was deleted from the database
        assert not Order.objects.filter(transaction_id=order_to_delete.transaction_id).exists()
    
    def test_get_status_counts(self):
        """Test GET request to order status counts endpoint."""
        # Create orders with different statuses
        OrderFactory(status='draft')
        OrderFactory(status='draft')
        OrderFactory(status='submitted')
        OrderFactory(status='shipped')
        OrderFactory(status='delivered')
        OrderFactory(status='cancelled')
        
        # Make the request
        url = reverse('order-status-counts')
        response = self.client.get(url)
        
        # Verify the response
        assert response.status_code == 200
        assert response.data['success'] is True
        assert 'data' in response.data
        
        # Check counts
        counts = response.data['data']
        assert counts['draft'] >= 3  # 2 new + 1 from setup
        assert counts['submitted'] >= 1
        assert counts['shipped'] >= 1
        assert counts['delivered'] >= 1
        assert counts['cancelled'] >= 1
    
    def test_get_choices(self):
        """Test GET request to order choices endpoint."""
        # Make the request
        url = reverse('order-choices')
        response = self.client.get(url)
        
        # Verify the response
        assert response.status_code == 200
        assert response.data['success'] is True
        assert 'data' in response.data
        
        # Check choices
        choices = response.data['data']
        assert 'status_choices' in choices
        assert 'priority_choices' in choices
        
        # Verify all status choices are included
        status_values = [choice['value'] for choice in choices['status_choices']]
        assert 'draft' in status_values
        assert 'submitted' in status_values
        assert 'shipped' in status_values
        assert 'delivered' in status_values
        assert 'cancelled' in status_values
        
        # Verify all priority choices are included
        priority_values = [choice['value'] for choice in choices['priority_choices']]
        assert 'low' in priority_values
        assert 'medium' in priority_values
        assert 'high' in priority_values
    
    @pytest.mark.skip(reason="Full PACT verification requires a running service")
    def test_verify_order_pacts(self):
        """Verify all PACT contracts for the order API."""
        # This test requires a running API service
        if not os.path.exists(PACT_FILE):
            pytest.skip(f"PACT file not found: {PACT_FILE}")
        
        # Use the Pact verifier to validate all contracts
        verifier = Verifier(
            provider="order-api",
            provider_base_url=PROVIDER_URL
        )
        
        # Define provider states and set up the required state
        provider_states = {
            "an order exists": self.setup_order_exists,
            "multiple orders exist": self.setup_multiple_orders,
            "orders in different statuses exist": self.setup_orders_with_different_statuses
        }
        
        # Verify the PACT
        output, _ = verifier.verify_pacts(
            PACT_FILE,
            provider_states=provider_states,
            provider_states_setup_url=f"{PROVIDER_URL}/_pact/provider_states"
        )
        
        assert output == 0, "PACT verification failed"
    
    def setup_order_exists(self):
        """Set up the 'an order exists' provider state."""
        # Create a test order with predictable data
        customer = CustomerFactory(company_name="PACT Test Company")
        return OrderFactory(
            transaction_id=999999,
            customer=customer,
            reference_number="PACT-REF-001",
            status="draft",
            sku_quantity={"PACT-SKU-001": 10}
        )
    
    def setup_multiple_orders(self):
        """Set up the 'multiple orders exist' provider state."""
        # Create multiple test orders
        customer = CustomerFactory(company_name="PACT Test Company")
        orders = []
        for i in range(5):
            orders.append(OrderFactory(
                customer=customer,
                reference_number=f"PACT-REF-{i+1:03d}",
                status="draft"
            ))
        return orders
    
    def setup_orders_with_different_statuses(self):
        """Set up the 'orders in different statuses exist' provider state."""
        # Create orders with different statuses
        customer = CustomerFactory(company_name="PACT Status Company")
        return {
            'draft': OrderFactory(customer=customer, status='draft'),
            'submitted': SubmittedOrderFactory(customer=customer),
            'shipped': ShippedOrderFactory(customer=customer)
        }