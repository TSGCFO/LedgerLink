# shipping/tests/test_views.py

import pytest
from datetime import datetime, timedelta
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from shipping.models import CADShipping, USShipping
from .factories import CADShippingFactory, USShippingFactory
from orders.tests.factories import OrderFactory
from customers.tests.factories import CustomerFactory

pytestmark = pytest.mark.django_db

class TestCADShippingViewSet:
    """
    Test cases for the CADShippingViewSet.
    """
    
    @pytest.fixture
    def api_client(self):
        return APIClient()
    
    def test_list_cad_shipping(self, api_client):
        """Test listing CAD shipping records."""
        # Create multiple shipping records
        shipping_records = [CADShippingFactory.create() for _ in range(3)]
        
        # Make API request
        url = reverse('cadshipping-list')
        response = api_client.get(url)
        
        # Assertions
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert len(response.data['data']) == 3
        
        # Verify tracking numbers match
        tracking_numbers = [s['tracking_number'] for s in response.data['data']]
        expected_tracking_numbers = [s.tracking_number for s in shipping_records]
        for tn in expected_tracking_numbers:
            assert tn in tracking_numbers
    
    def test_retrieve_cad_shipping(self, api_client):
        """Test retrieving a single CAD shipping record."""
        shipping = CADShippingFactory.create()
        
        url = reverse('cadshipping-detail', kwargs={'pk': shipping.pk})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['transaction'] == shipping.transaction_id
        assert response.data['tracking_number'] == shipping.tracking_number
        assert response.data['ship_to_name'] == shipping.ship_to_name
    
    def test_create_cad_shipping(self, api_client):
        """Test creating a CAD shipping record."""
        order = OrderFactory.create()
        customer = order.customer
        
        url = reverse('cadshipping-list')
        data = {
            'transaction': order.id,
            'customer': customer.id,
            'ship_to_name': 'Test Name',
            'ship_to_address_1': '123 Test St',
            'ship_to_city': 'Test City',
            'ship_to_state': 'TS',
            'ship_to_postal_code': 'A1B 2C3',
            'tracking_number': 'TRACK-1234567890',
            'pre_tax_shipping_charge': '25.50',
            'carrier': 'FedEx'
        }
        
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['success'] is True
        assert response.data['message'] == 'CAD shipping record created successfully'
        assert response.data['data']['tracking_number'] == 'TRACK-1234567890'
        
        # Verify record was actually created in db
        assert CADShipping.objects.filter(transaction_id=order.id).exists()
    
    def test_update_cad_shipping(self, api_client):
        """Test updating a CAD shipping record."""
        shipping = CADShippingFactory.create()
        
        url = reverse('cadshipping-detail', kwargs={'pk': shipping.pk})
        data = {
            'ship_to_name': 'Updated Name',
            'tracking_number': 'UPDATED-TRACK-9876',
            'carrier': 'UPS'
        }
        
        response = api_client.patch(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert response.data['message'] == 'CAD shipping record updated successfully'
        assert response.data['data']['ship_to_name'] == 'Updated Name'
        assert response.data['data']['tracking_number'] == 'UPDATED-TRACK-9876'
        assert response.data['data']['carrier'] == 'UPS'
        
        # Verify record was actually updated in db
        shipping.refresh_from_db()
        assert shipping.ship_to_name == 'Updated Name'
        assert shipping.tracking_number == 'UPDATED-TRACK-9876'
        assert shipping.carrier == 'UPS'
    
    def test_delete_cad_shipping(self, api_client):
        """Test deleting a CAD shipping record."""
        shipping = CADShippingFactory.create()
        
        url = reverse('cadshipping-detail', kwargs={'pk': shipping.pk})
        response = api_client.delete(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert response.data['message'] == 'CAD shipping record deleted successfully'
        
        # Verify record was actually deleted from db
        assert not CADShipping.objects.filter(pk=shipping.pk).exists()
    
    def test_filter_by_customer(self, api_client):
        """Test filtering CAD shipping records by customer."""
        customer1 = CustomerFactory.create()
        customer2 = CustomerFactory.create()
        
        # Create orders for different customers
        order1 = OrderFactory.create(customer=customer1)
        order2 = OrderFactory.create(customer=customer1)
        order3 = OrderFactory.create(customer=customer2)
        
        # Create shipping records
        shipping1 = CADShippingFactory.create(transaction=order1, customer=customer1)
        shipping2 = CADShippingFactory.create(transaction=order2, customer=customer1)
        shipping3 = CADShippingFactory.create(transaction=order3, customer=customer2)
        
        # Filter for customer1
        url = reverse('cadshipping-list')
        response = api_client.get(f"{url}?customer={customer1.id}")
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['data']) == 2
        
        # Check that only customer1's records are returned
        customer_ids = [s['customer'] for s in response.data['data']]
        assert all(cid == customer1.id for cid in customer_ids)
    
    def test_filter_by_order(self, api_client):
        """Test filtering CAD shipping records by order."""
        # Create multiple shipping records
        shipping1 = CADShippingFactory.create()
        shipping2 = CADShippingFactory.create()
        
        # Filter for specific order
        url = reverse('cadshipping-list')
        response = api_client.get(f"{url}?transaction={shipping1.transaction_id}")
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['data']) == 1
        assert response.data['data'][0]['transaction'] == shipping1.transaction_id
    
    def test_search_cad_shipping(self, api_client):
        """Test searching CAD shipping records."""
        # Create shipping records with specific values
        CADShippingFactory.create(tracking_number="ABC12345", ship_to_name="John Doe")
        CADShippingFactory.create(tracking_number="XYZ67890", ship_to_name="Jane Smith")
        CADShippingFactory.create(reference="REF-12345")
        
        # Search for 'ABC'
        url = reverse('cadshipping-list')
        response = api_client.get(f"{url}?search=ABC")
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['data']) == 1
        assert response.data['data'][0]['tracking_number'] == "ABC12345"
        
        # Search for 'Smith'
        response = api_client.get(f"{url}?search=Smith")
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['data']) == 1
        assert response.data['data'][0]['ship_to_name'] == "Jane Smith"
        
        # Search for 'REF'
        response = api_client.get(f"{url}?search=REF")
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['data']) == 1
        assert response.data['data'][0]['reference'] == "REF-12345"
    
    def test_filter_by_date_range(self, api_client):
        """Test filtering CAD shipping records by date range."""
        # Create shipping records with different dates
        today = datetime.now()
        CADShippingFactory.create(ship_date=today - timedelta(days=10))
        CADShippingFactory.create(ship_date=today - timedelta(days=5))
        CADShippingFactory.create(ship_date=today)
        
        # Filter for specific date range
        start_date = (today - timedelta(days=7)).strftime('%Y-%m-%d')
        end_date = today.strftime('%Y-%m-%d')
        
        url = reverse('cadshipping-list')
        response = api_client.get(f"{url}?start_date={start_date}&end_date={end_date}")
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['data']) == 2  # Should include the 5-day old and today's records
    
    def test_carriers_action(self, api_client):
        """Test the carriers action."""
        # Create shipping records with different carriers
        CADShippingFactory.create(carrier="FedEx")
        CADShippingFactory.create(carrier="UPS")
        CADShippingFactory.create(carrier="FedEx")  # Duplicate to test distinct
        
        url = reverse('cadshipping-carriers')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert len(response.data['data']) == 2  # Should have two unique carriers
        assert "FedEx" in response.data['data']
        assert "UPS" in response.data['data']


class TestUSShippingViewSet:
    """
    Test cases for the USShippingViewSet.
    """
    
    @pytest.fixture
    def api_client(self):
        return APIClient()
    
    def test_list_us_shipping(self, api_client):
        """Test listing US shipping records."""
        # Create multiple shipping records
        shipping_records = [USShippingFactory.create() for _ in range(3)]
        
        # Make API request
        url = reverse('usshipping-list')
        response = api_client.get(url)
        
        # Assertions
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert len(response.data['data']) == 3
        
        # Verify tracking numbers match
        tracking_numbers = [s['tracking_number'] for s in response.data['data']]
        expected_tracking_numbers = [s.tracking_number for s in shipping_records]
        for tn in expected_tracking_numbers:
            assert tn in tracking_numbers
    
    def test_retrieve_us_shipping(self, api_client):
        """Test retrieving a single US shipping record."""
        shipping = USShippingFactory.create()
        
        url = reverse('usshipping-detail', kwargs={'pk': shipping.pk})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['transaction'] == shipping.transaction_id
        assert response.data['tracking_number'] == shipping.tracking_number
        assert response.data['ship_to_name'] == shipping.ship_to_name
    
    def test_create_us_shipping(self, api_client):
        """Test creating a US shipping record."""
        order = OrderFactory.create()
        customer = order.customer
        
        url = reverse('usshipping-list')
        data = {
            'transaction': order.id,
            'customer': customer.id,
            'ship_to_name': 'US Test Name',
            'ship_to_address_1': '456 Test Ave',
            'ship_to_city': 'Test City',
            'ship_to_state': 'CA',
            'ship_to_zip': '90210',
            'tracking_number': 'US-TRACK-1234567890',
            'service_name': 'Express'
        }
        
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['success'] is True
        assert response.data['message'] == 'US shipping record created successfully'
        assert response.data['data']['tracking_number'] == 'US-TRACK-1234567890'
        
        # Verify record was actually created in db
        assert USShipping.objects.filter(transaction_id=order.id).exists()
    
    def test_update_us_shipping(self, api_client):
        """Test updating a US shipping record."""
        shipping = USShippingFactory.create()
        
        url = reverse('usshipping-detail', kwargs={'pk': shipping.pk})
        data = {
            'ship_to_name': 'Updated US Name',
            'tracking_number': 'UPDATED-US-TRACK-9876',
            'service_name': '2-Day'
        }
        
        response = api_client.patch(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert response.data['message'] == 'US shipping record updated successfully'
        assert response.data['data']['ship_to_name'] == 'Updated US Name'
        assert response.data['data']['tracking_number'] == 'UPDATED-US-TRACK-9876'
        assert response.data['data']['service_name'] == '2-Day'
        
        # Verify record was actually updated in db
        shipping.refresh_from_db()
        assert shipping.ship_to_name == 'Updated US Name'
        assert shipping.tracking_number == 'UPDATED-US-TRACK-9876'
        assert shipping.service_name == '2-Day'
    
    def test_delete_us_shipping(self, api_client):
        """Test deleting a US shipping record."""
        shipping = USShippingFactory.create()
        
        url = reverse('usshipping-detail', kwargs={'pk': shipping.pk})
        response = api_client.delete(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert response.data['message'] == 'US shipping record deleted successfully'
        
        # Verify record was actually deleted from db
        assert not USShipping.objects.filter(pk=shipping.pk).exists()
    
    def test_filter_by_status(self, api_client):
        """Test filtering US shipping records by status."""
        # Create shipping records with different statuses
        USShippingFactory.create(current_status="In Transit", delivery_status="Pending")
        USShippingFactory.create(current_status="In Transit", delivery_status="Pending")
        USShippingFactory.create(current_status="Delivered", delivery_status="Completed")
        
        # Filter by current status
        url = reverse('usshipping-list')
        response = api_client.get(f"{url}?current_status=In Transit")
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['data']) == 2
        for record in response.data['data']:
            assert record['current_status'] == "In Transit"
        
        # Filter by delivery status
        response = api_client.get(f"{url}?delivery_status=Completed")
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['data']) == 1
        assert response.data['data'][0]['delivery_status'] == "Completed"
    
    def test_search_us_shipping(self, api_client):
        """Test searching US shipping records."""
        # Create shipping records with specific values
        USShippingFactory.create(tracking_number="US-ABC-12345", ship_to_name="John Doe")
        USShippingFactory.create(tracking_number="US-XYZ-67890", ship_to_name="Jane Smith")
        USShippingFactory.create(service_name="Express Priority")
        
        # Search for 'ABC'
        url = reverse('usshipping-list')
        response = api_client.get(f"{url}?search=ABC")
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['data']) == 1
        assert response.data['data'][0]['tracking_number'] == "US-ABC-12345"
        
        # Search for 'Smith'
        response = api_client.get(f"{url}?search=Smith")
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['data']) == 1
        assert response.data['data'][0]['ship_to_name'] == "Jane Smith"
        
        # Search for 'Priority'
        response = api_client.get(f"{url}?search=Priority")
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['data']) == 1
        assert response.data['data'][0]['service_name'] == "Express Priority"
    
    def test_statuses_action(self, api_client):
        """Test the statuses action."""
        # Create shipping records with different statuses
        USShippingFactory.create(current_status="In Transit", delivery_status="Pending")
        USShippingFactory.create(current_status="Delivered", delivery_status="Completed")
        USShippingFactory.create(current_status="Exception", delivery_status="Failed")
        
        url = reverse('usshipping-statuses')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        
        # Check current statuses
        assert len(response.data['data']['current_statuses']) == 3
        assert "In Transit" in response.data['data']['current_statuses']
        assert "Delivered" in response.data['data']['current_statuses']
        assert "Exception" in response.data['data']['current_statuses']
        
        # Check delivery statuses
        assert len(response.data['data']['delivery_statuses']) == 3
        assert "Pending" in response.data['data']['delivery_statuses']
        assert "Completed" in response.data['data']['delivery_statuses']
        assert "Failed" in response.data['data']['delivery_statuses']
    
    def test_service_names_action(self, api_client):
        """Test the service_names action."""
        # Create shipping records with different service names
        USShippingFactory.create(service_name="Ground")
        USShippingFactory.create(service_name="Express")
        USShippingFactory.create(service_name="2-Day")
        USShippingFactory.create(service_name="Express")  # Duplicate to test distinct
        
        url = reverse('usshipping-service-names')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert len(response.data['data']) == 3  # Should have three unique service names
        assert "Ground" in response.data['data']
        assert "Express" in response.data['data']
        assert "2-Day" in response.data['data']