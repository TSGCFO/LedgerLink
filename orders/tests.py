from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
import json

from .models import Order, OrderSKUView
from .serializers import OrderSerializer
from customers.models import Customer


# Mock for OrderSKUView since it's a DB view
class MockOrderSKUView:
    def __init__(self, transaction_id, sku_name, cases, picks, case_size=None, case_unit=None):
        self.transaction_id = transaction_id
        self.sku_name = sku_name
        self.cases = cases
        self.picks = picks
        self.case_size = case_size
        self.case_unit = case_unit

    def values(self, *args):
        return [{
            'sku_name': self.sku_name,
            'cases': self.cases,
            'picks': self.picks,
            'case_size': self.case_size,
            'case_unit': self.case_unit
        }]


class OrderModelTests(TestCase):
    """Test cases for the Order model"""

    def setUp(self):
        """Set up test data"""
        self.customer = Customer.objects.create(
            company_name="Test Company",
            contact_name="John Doe",
            contact_email="john@example.com",
            contact_phone="123-456-7890"
        )
        
        self.order = Order.objects.create(
            transaction_id=12345,
            customer=self.customer,
            reference_number="REF-001",
            ship_to_name="Recipient Name",
            ship_to_address="123 Test St",
            ship_to_city="Test City",
            ship_to_state="TS",
            ship_to_zip="12345",
            sku_quantity={"SKU1": 10, "SKU2": 5},
            total_item_qty=15,
            line_items=2,
            status="draft",
            priority="medium"
        )

    def test_create_order(self):
        """Test creating an Order instance"""
        self.assertEqual(self.order.transaction_id, 12345)
        self.assertEqual(self.order.customer, self.customer)
        self.assertEqual(self.order.reference_number, "REF-001")
        self.assertEqual(self.order.ship_to_name, "Recipient Name")
        self.assertEqual(self.order.sku_quantity, {"SKU1": 10, "SKU2": 5})
        self.assertEqual(self.order.total_item_qty, 15)
        self.assertEqual(self.order.line_items, 2)
        self.assertEqual(self.order.status, "draft")
        self.assertEqual(self.order.priority, "medium")

    def test_order_str_representation(self):
        """Test the string representation of an Order"""
        self.assertEqual(str(self.order), f"Order {self.order.transaction_id} for {self.customer}")
    
    def test_status_choices(self):
        """Test the status choices are correctly defined"""
        choices = [choice[0] for choice in Order.STATUS_CHOICES]
        self.assertIn('draft', choices)
        self.assertIn('submitted', choices)
        self.assertIn('shipped', choices)
        self.assertIn('delivered', choices)
        self.assertIn('cancelled', choices)
        
    def test_priority_choices(self):
        """Test the priority choices are correctly defined"""
        choices = [choice[0] for choice in Order.PRIORITY_CHOICES]
        self.assertIn('low', choices)
        self.assertIn('medium', choices)
        self.assertIn('high', choices)
        
    def test_default_status_and_priority(self):
        """Test default values for status and priority"""
        # Create order without specifying status and priority
        order = Order.objects.create(
            transaction_id=54321,
            customer=self.customer,
            reference_number="REF-002"
        )
        self.assertEqual(order.status, 'draft')
        self.assertEqual(order.priority, 'medium')
    
    # Mock the OrderSKUView for testing order methods
    def test_get_sku_details(self, monkeypatch):
        """Test get_sku_details method"""
        # Mock the queryset returned by OrderSKUView
        mock_results = [
            MockOrderSKUView(self.order.transaction_id, "SKU1", 2, 6, 12, "case"),
            MockOrderSKUView(self.order.transaction_id, "SKU2", 1, 2, 8, "box")
        ]
        
        # Patch the filter method to return our mock results
        def mock_filter(*args, **kwargs):
            class MockQuerySet:
                def exclude(self, **kwargs):
                    if 'sku_name__in' in kwargs:
                        return [m for m in mock_results if m.sku_name not in kwargs['sku_name__in']]
                    return mock_results
                
                def aggregate(self, **kwargs):
                    if 'total_cases' in kwargs:
                        return {'total_cases': sum(m.cases for m in mock_results)}
                    elif 'total_picks' in kwargs:
                        return {'total_picks': sum(m.picks for m in mock_results)}
                    return {}
                
                def exists(self):
                    return len(mock_results) > 0
                
                def values(self, *args):
                    result = []
                    for m in mock_results:
                        item = {}
                        for arg in args:
                            item[arg] = getattr(m, arg)
                        result.append(item)
                    return result
            
            return MockQuerySet()
        
        # Apply the monkeypatch
        with monkeypatch.context() as m:
            m.setattr(OrderSKUView.objects, 'filter', mock_filter)
            
            # Test get_sku_details
            details = self.order.get_sku_details()
            self.assertEqual(len(details), 2)
            
            # Test with exclude_skus
            details = self.order.get_sku_details(exclude_skus=["SKU1"])
            self.assertEqual(len(details), 1)
            
            # Test get_total_cases
            total_cases = self.order.get_total_cases()
            self.assertEqual(total_cases, 3)  # 2 + 1
            
            # Test get_total_picks
            total_picks = self.order.get_total_picks()
            self.assertEqual(total_picks, 8)  # 6 + 2
            
            # Test get_case_summary
            summary = self.order.get_case_summary()
            self.assertEqual(summary['total_cases'], 3)
            self.assertEqual(summary['total_picks'], 8)
            self.assertEqual(len(summary['sku_breakdown']), 2)
            
            # Test has_only_excluded_skus
            result = self.order.has_only_excluded_skus(["SKU1", "SKU2"])
            self.assertTrue(result)
            
            result = self.order.has_only_excluded_skus(["SKU1"])
            self.assertFalse(result)


class OrderSerializerTests(TestCase):
    """Test cases for the OrderSerializer"""

    def setUp(self):
        """Set up test data"""
        self.customer = Customer.objects.create(
            company_name="Test Company",
            contact_name="John Doe",
            contact_email="john@example.com",
            contact_phone="123-456-7890"
        )
        
        self.order_data = {
            'customer': self.customer.id,
            'reference_number': 'REF-001',
            'ship_to_name': 'Recipient Name',
            'ship_to_address': '123 Test St',
            'ship_to_city': 'Test City',
            'ship_to_state': 'TS',
            'ship_to_zip': '12345',
            'sku_quantity': {'SKU1': 10, 'SKU2': 5},
            'status': 'draft',
            'priority': 'medium'
        }
        
        self.order = Order.objects.create(
            transaction_id=12345,
            customer=self.customer,
            reference_number="REF-001",
            ship_to_name="Recipient Name",
            ship_to_address="123 Test St",
            ship_to_city="Test City",
            ship_to_state="TS",
            ship_to_zip="12345",
            sku_quantity={"SKU1": 10, "SKU2": 5},
            total_item_qty=15,
            line_items=2,
            status="draft",
            priority="medium"
        )

    def test_serializer_valid_data(self):
        """Test serializer with valid data"""
        serializer = OrderSerializer(data=self.order_data)
        self.assertTrue(serializer.is_valid())
        
    def test_serializer_missing_required_field(self):
        """Test serializer with missing required field"""
        # Missing 'reference_number' field
        invalid_data = self.order_data.copy()
        del invalid_data['reference_number']
        serializer = OrderSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('reference_number', serializer.errors)
        
    def test_sku_quantity_validation_valid(self):
        """Test SKU quantity validation with valid data"""
        valid_sku_data = {
            'customer': self.customer.id,
            'reference_number': 'REF-001',
            'sku_quantity': {'SKU1': 10, 'SKU2': 5}
        }
        serializer = OrderSerializer(data=valid_sku_data)
        self.assertTrue(serializer.is_valid())
        
    def test_sku_quantity_validation_invalid_format(self):
        """Test SKU quantity validation with invalid format"""
        # Not a dictionary
        invalid_sku_data = {
            'customer': self.customer.id,
            'reference_number': 'REF-001',
            'sku_quantity': ['SKU1', 10]  # List instead of dict
        }
        serializer = OrderSerializer(data=invalid_sku_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('sku_quantity', serializer.errors)
        
    def test_sku_quantity_validation_invalid_quantities(self):
        """Test SKU quantity validation with invalid quantities"""
        # Negative quantity
        invalid_sku_data = {
            'customer': self.customer.id,
            'reference_number': 'REF-001',
            'sku_quantity': {'SKU1': -5}  # Negative quantity
        }
        serializer = OrderSerializer(data=invalid_sku_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('sku_quantity', serializer.errors)
        
        # Zero quantity
        invalid_sku_data = {
            'customer': self.customer.id,
            'reference_number': 'REF-001',
            'sku_quantity': {'SKU1': 0}  # Zero quantity
        }
        serializer = OrderSerializer(data=invalid_sku_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('sku_quantity', serializer.errors)
        
    def test_shipping_address_validation(self):
        """Test shipping address validation"""
        # Missing required shipping fields
        invalid_shipping_data = {
            'customer': self.customer.id,
            'reference_number': 'REF-001',
            'ship_to_name': 'Recipient Name',
            # Missing other required shipping fields
        }
        serializer = OrderSerializer(data=invalid_shipping_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('shipping', serializer.errors)
        
    def test_serializer_autocalculates_item_quantities(self):
        """Test that serializer automatically calculates total_item_qty and line_items"""
        serializer = OrderSerializer(data=self.order_data)
        self.assertTrue(serializer.is_valid())
        
        # Check that validated_data contains calculated fields
        self.assertEqual(serializer.validated_data['total_item_qty'], 15)  # 10 + 5
        self.assertEqual(serializer.validated_data['line_items'], 2)
        
    def test_status_transition_validation(self):
        """Test status transition validation"""
        # Create an order in 'draft' status
        order = Order.objects.create(
            transaction_id=54321,
            customer=self.customer,
            reference_number='REF-002',
            status='draft'
        )
        
        # Valid transition: draft -> submitted
        valid_data = {'status': 'submitted', 'customer': self.customer.id}
        serializer = OrderSerializer(instance=order, data=valid_data, partial=True)
        self.assertTrue(serializer.is_valid())
        
        # Invalid transition: draft -> delivered (skipping steps)
        invalid_data = {'status': 'delivered', 'customer': self.customer.id}
        serializer = OrderSerializer(instance=order, data=invalid_data, partial=True)
        self.assertFalse(serializer.is_valid())
        self.assertIn('status', serializer.errors)
        
        # Create a cancelled order
        cancelled_order = Order.objects.create(
            transaction_id=67890,
            customer=self.customer,
            reference_number='REF-003',
            status='cancelled'
        )
        
        # Attempt to change status of cancelled order
        invalid_data = {'status': 'submitted', 'customer': self.customer.id}
        serializer = OrderSerializer(instance=cancelled_order, data=invalid_data, partial=True)
        self.assertFalse(serializer.is_valid())
        self.assertIn('status', serializer.errors)
        
    def test_transaction_id_generation(self):
        """Test transaction_id generation in create method"""
        serializer = OrderSerializer(data=self.order_data)
        self.assertTrue(serializer.is_valid())
        order = serializer.save()
        
        # Verify transaction_id was generated
        self.assertIsNotNone(order.transaction_id)
        self.assertTrue(order.transaction_id > 0)


class OrderAPITests(APITestCase):
    """Test cases for the Order API endpoints"""

    def setUp(self):
        """Set up test data and authenticate"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        # Create customers
        self.customer = Customer.objects.create(
            company_name="Test Company",
            contact_name="John Doe",
            contact_email="john@example.com",
            contact_phone="123-456-7890"
        )
        
        self.another_customer = Customer.objects.create(
            company_name="Another Company",
            contact_name="Jane Smith",
            contact_email="jane@example.com",
            contact_phone="987-654-3210"
        )
        
        # Create orders with different statuses
        self.order_draft = Order.objects.create(
            transaction_id=12345,
            customer=self.customer,
            reference_number="REF-DRAFT",
            ship_to_name="Recipient Draft",
            ship_to_address="123 Draft St",
            ship_to_city="Draft City",
            ship_to_state="DC",
            ship_to_zip="12345",
            sku_quantity={"SKU1": 10, "SKU2": 5},
            total_item_qty=15,
            line_items=2,
            status="draft",
            priority="low"
        )
        
        self.order_submitted = Order.objects.create(
            transaction_id=23456,
            customer=self.customer,
            reference_number="REF-SUBMITTED",
            ship_to_name="Recipient Submitted",
            ship_to_address="123 Submitted St",
            ship_to_city="Submitted City",
            ship_to_state="SC",
            ship_to_zip="23456",
            sku_quantity={"SKU3": 8, "SKU4": 12},
            total_item_qty=20,
            line_items=2,
            status="submitted",
            priority="medium"
        )
        
        self.order_shipped = Order.objects.create(
            transaction_id=34567,
            customer=self.another_customer,
            reference_number="REF-SHIPPED",
            ship_to_name="Recipient Shipped",
            ship_to_address="123 Shipped St",
            ship_to_city="Shipped City",
            ship_to_state="SC",
            ship_to_zip="34567",
            sku_quantity={"SKU5": 15},
            total_item_qty=15,
            line_items=1,
            status="shipped",
            priority="high"
        )
        
        # URLs for API endpoints
        self.list_url = reverse('order-list')
        self.detail_url = reverse('order-detail', kwargs={'pk': self.order_draft.pk})
        self.cancel_url = reverse('order-cancel', kwargs={'pk': self.order_draft.pk})
        self.status_counts_url = reverse('order-status-counts')
        self.choices_url = reverse('order-choices')

    def test_get_order_list(self):
        """Test GET request to retrieve all orders"""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(len(response.data['data']), 3)
        
    def test_filter_by_customer(self):
        """Test filtering orders by customer"""
        url = f"{self.list_url}?customer={self.customer.id}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 2)
        
    def test_filter_by_status(self):
        """Test filtering orders by status"""
        url = f"{self.list_url}?status=draft"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['status'], 'draft')
        
    def test_filter_by_priority(self):
        """Test filtering orders by priority"""
        url = f"{self.list_url}?priority=high"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['priority'], 'high')
        
    def test_search_functionality(self):
        """Test searching orders"""
        # Search by reference number
        url = f"{self.list_url}?search=SUBMITTED"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['reference_number'], 'REF-SUBMITTED')
        
        # Search by ship_to_name
        url = f"{self.list_url}?search=Recipient Draft"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['ship_to_name'], 'Recipient Draft')
        
    def test_get_order_detail(self):
        """Test retrieving a specific order"""
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['transaction_id'], self.order_draft.transaction_id)
        self.assertEqual(response.data['status'], 'draft')
        
    def test_create_order(self):
        """Test creating a new order"""
        data = {
            'customer': self.customer.id,
            'reference_number': 'REF-NEW',
            'ship_to_name': 'New Recipient',
            'ship_to_address': '456 New St',
            'ship_to_city': 'New City',
            'ship_to_state': 'NS',
            'ship_to_zip': '45678',
            'sku_quantity': {'SKU6': 25, 'SKU7': 10},
            'priority': 'high'
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        
        # Verify record was created
        self.assertEqual(Order.objects.count(), 4)
        
        # Verify total_item_qty and line_items were calculated
        new_order_id = response.data['data']['transaction_id']
        new_order = Order.objects.get(transaction_id=new_order_id)
        self.assertEqual(new_order.total_item_qty, 35)  # 25 + 10
        self.assertEqual(new_order.line_items, 2)
        
    def test_update_order(self):
        """Test updating an order"""
        data = {
            'reference_number': 'REF-UPDATED',
            'customer': self.customer.id,
            'status': 'submitted'  # Valid transition from draft
        }
        response = self.client.patch(self.detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        # Verify record was updated
        self.order_draft.refresh_from_db()
        self.assertEqual(self.order_draft.reference_number, 'REF-UPDATED')
        self.assertEqual(self.order_draft.status, 'submitted')
        
    def test_invalid_status_transition(self):
        """Test invalid status transition"""
        data = {
            'customer': self.customer.id,
            'status': 'delivered'  # Invalid transition from draft (skipping steps)
        }
        response = self.client.patch(self.detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        
    def test_delete_draft_order(self):
        """Test deleting a draft order"""
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        # Verify record was deleted
        self.assertFalse(Order.objects.filter(transaction_id=self.order_draft.transaction_id).exists())
        
    def test_delete_submitted_order(self):
        """Test deleting a submitted order (should fail)"""
        url = reverse('order-detail', kwargs={'pk': self.order_submitted.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        
        # Verify record was not deleted
        self.assertTrue(Order.objects.filter(transaction_id=self.order_submitted.transaction_id).exists())
        
    def test_cancel_order(self):
        """Test cancelling an order"""
        response = self.client.post(self.cancel_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        # Verify order was cancelled
        self.order_draft.refresh_from_db()
        self.assertEqual(self.order_draft.status, 'cancelled')
        
    def test_cannot_cancel_delivered_order(self):
        """Test that a delivered order cannot be cancelled"""
        # Create a delivered order
        delivered_order = Order.objects.create(
            transaction_id=45678,
            customer=self.customer,
            reference_number="REF-DELIVERED",
            status="delivered"
        )
        
        url = reverse('order-cancel', kwargs={'pk': delivered_order.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        
        # Verify status was not changed
        delivered_order.refresh_from_db()
        self.assertEqual(delivered_order.status, 'delivered')
        
    def test_status_counts_action(self):
        """Test the status_counts custom action"""
        response = self.client.get(self.status_counts_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        # Should return counts for each status
        counts = response.data['data']
        self.assertEqual(counts['draft'], 1)
        self.assertEqual(counts['submitted'], 1)
        self.assertEqual(counts['shipped'], 1)
        self.assertEqual(counts['delivered'], 0)
        self.assertEqual(counts['cancelled'], 0)
        
    def test_choices_action(self):
        """Test the choices custom action"""
        response = self.client.get(self.choices_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        # Should return lists of status and priority choices
        self.assertIn('status_choices', response.data['data'])
        self.assertIn('priority_choices', response.data['data'])
        
        # Verify format of choices
        status_choices = response.data['data']['status_choices']
        self.assertTrue(len(status_choices) > 0)
        self.assertIn('value', status_choices[0])
        self.assertIn('label', status_choices[0])
        
        # Verify specific choice values
        status_values = [choice['value'] for choice in status_choices]
        self.assertIn('draft', status_values)
        self.assertIn('submitted', status_values)
        self.assertIn('shipped', status_values)
        self.assertIn('delivered', status_values)
        self.assertIn('cancelled', status_values)
        
    def test_unauthorized_access(self):
        """Test unauthorized access to the API"""
        self.client.logout()
        
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
