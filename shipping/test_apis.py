"""
Tests for the shipping API endpoints.
"""

import pytest
from decimal import Decimal
from datetime import date, timedelta
from django.urls import reverse
from rest_framework import status

from .models import CADShipping, USShipping
from test_utils.factories import (
    OrderFactory, CustomerFactory, CADShippingFactory, USShippingFactory, UserFactory
)
from test_utils.mixins import APITestMixin

pytestmark = pytest.mark.django_db


class TestCADShippingAPI(APITestMixin):
    """Tests for the CAD shipping API endpoints."""

    def setUp(self):
        super().setUp()
        self.customer = CustomerFactory(created_by=self.user)
        self.order = OrderFactory(customer=self.customer, created_by=self.user)
        self.cad_shipping = CADShippingFactory(
            transaction=self.order,
            customer=self.customer,
            ship_to_name="Test Recipient",
            ship_to_postal_code="A1B 2C3",
            carrier="Canada Post",
            tracking_number="CAD12345678"
        )
        
        self.list_url = reverse('cadshipping-list')
        self.detail_url = reverse('cadshipping-detail', kwargs={'pk': self.cad_shipping.pk})
        self.carriers_url = reverse('cadshipping-carriers')

    def test_list_cad_shipping(self):
        """Test retrieving a list of CAD shipping records."""
        # Create additional shipping records
        order2 = OrderFactory(customer=self.customer, created_by=self.user)
        order3 = OrderFactory(customer=self.customer, created_by=self.user)
        CADShippingFactory(transaction=order2, customer=self.customer, carrier="UPS")
        CADShippingFactory(transaction=order3, customer=self.customer, carrier="FedEx")
        
        # Get all shipping records
        response = self.get_json_response(self.list_url)
        
        # Check response
        assert response['success'] is True
        assert len(response['data']) == 3

    def test_filter_by_customer(self):
        """Test filtering shipping records by customer."""
        # Create another customer and shipping record
        customer2 = CustomerFactory(created_by=self.user)
        order2 = OrderFactory(customer=customer2, created_by=self.user)
        CADShippingFactory(transaction=order2, customer=customer2)
        
        # Filter by first customer
        url = f"{self.list_url}?customer={self.customer.pk}"
        response = self.get_json_response(url)
        
        # Check response
        assert response['success'] is True
        assert len(response['data']) == 1
        assert response['data'][0]['customer'] == self.customer.pk

    def test_filter_by_carrier(self):
        """Test filtering shipping records by carrier."""
        # Create additional shipping records with different carriers
        order2 = OrderFactory(customer=self.customer, created_by=self.user)
        CADShippingFactory(transaction=order2, customer=self.customer, carrier="Purolator")
        
        # Filter by carrier
        url = f"{self.list_url}?carrier=Purolator"
        response = self.get_json_response(url)
        
        # Check response
        assert response['success'] is True
        assert len(response['data']) == 1
        assert response['data'][0]['carrier'] == "Purolator"

    def test_search_by_tracking_number(self):
        """Test searching shipping records by tracking number."""
        # Create additional shipping records
        order2 = OrderFactory(customer=self.customer, created_by=self.user)
        CADShippingFactory(
            transaction=order2, 
            customer=self.customer, 
            tracking_number="SEARCHME123"
        )
        
        # Search by tracking number
        url = f"{self.list_url}?search=SEARCHME"
        response = self.get_json_response(url)
        
        # Check response
        assert response['success'] is True
        assert len(response['data']) == 1
        assert "SEARCHME" in response['data'][0]['tracking_number']

    def test_retrieve_cad_shipping(self):
        """Test retrieving a single CAD shipping record."""
        response = self.get_json_response(self.detail_url)
        
        # Check response
        assert response['success'] is True
        assert response['data']['transaction'] == self.order.pk
        assert response['data']['customer'] == self.customer.pk
        assert response['data']['ship_to_name'] == "Test Recipient"
        assert response['data']['ship_to_postal_code'] == "A1B 2C3"
        assert response['data']['carrier'] == "Canada Post"

    def test_create_cad_shipping(self):
        """Test creating a new CAD shipping record."""
        new_order = OrderFactory(customer=self.customer, created_by=self.user)
        
        data = {
            'transaction': new_order.pk,
            'customer': self.customer.pk,
            'ship_to_name': 'New Recipient',
            'ship_to_address_1': '123 New St',
            'ship_to_city': 'New City',
            'ship_to_state': 'NS',
            'ship_to_postal_code': 'B3C 4D5',
            'carrier': 'UPS',
            'tracking_number': 'NEWTRACK123',
            'pre_tax_shipping_charge': '15.99',
            'tax1type': 'GST',
            'tax1amount': '0.80'
        }
        
        response = self.get_json_response(
            self.list_url,
            method='post',
            data=data,
            status_code=status.HTTP_201_CREATED
        )
        
        # Check response
        assert response['success'] is True
        assert 'CAD shipping record created successfully' in response['message']
        assert response['data']['ship_to_name'] == 'New Recipient'
        assert response['data']['tracking_number'] == 'NEWTRACK123'
        
        # Check calculated fields
        assert Decimal(response['data']['total_tax']) == Decimal('0.80')
        assert Decimal(response['data']['total_charges']) == Decimal('16.79')
        
        # Verify in database
        assert CADShipping.objects.filter(transaction=new_order).exists()

    def test_update_cad_shipping(self):
        """Test updating a CAD shipping record."""
        data = {
            'ship_to_name': 'Updated Recipient',
            'tracking_number': 'UPDATED456',
            'pre_tax_shipping_charge': '20.50'
        }
        
        response = self.get_json_response(
            self.detail_url,
            method='patch',
            data=data
        )
        
        # Check response
        assert response['success'] is True
        assert 'CAD shipping record updated successfully' in response['message']
        assert response['data']['ship_to_name'] == 'Updated Recipient'
        assert response['data']['tracking_number'] == 'UPDATED456'
        
        # Verify in database
        self.cad_shipping.refresh_from_db()
        assert self.cad_shipping.ship_to_name == 'Updated Recipient'
        assert self.cad_shipping.tracking_number == 'UPDATED456'
        assert self.cad_shipping.pre_tax_shipping_charge == Decimal('20.50')

    def test_delete_cad_shipping(self):
        """Test deleting a CAD shipping record."""
        response = self.get_json_response(
            self.detail_url,
            method='delete'
        )
        
        # Check response
        assert response['success'] is True
        assert 'CAD shipping record deleted successfully' in response['message']
        
        # Verify in database
        assert not CADShipping.objects.filter(pk=self.cad_shipping.pk).exists()

    def test_validation_missing_required_fields(self):
        """Test validation for missing required shipping fields."""
        new_order = OrderFactory(customer=self.customer, created_by=self.user)
        
        # Missing some required fields
        data = {
            'transaction': new_order.pk,
            'customer': self.customer.pk,
            'ship_to_name': 'New Recipient',
            # Missing ship_to_address_1, ship_to_city, ship_to_state, ship_to_postal_code
        }
        
        response = self.get_json_response(
            self.list_url,
            method='post',
            data=data,
            status_code=status.HTTP_400_BAD_REQUEST
        )
        
        # Check response
        assert 'shipping' in response
        assert 'Missing required shipping fields' in response['shipping'][0]

    def test_get_carriers(self):
        """Test getting list of unique carriers."""
        # Create shipping records with different carriers
        order2 = OrderFactory(customer=self.customer, created_by=self.user)
        order3 = OrderFactory(customer=self.customer, created_by=self.user)
        CADShippingFactory(transaction=order2, customer=self.customer, carrier="UPS")
        CADShippingFactory(transaction=order3, customer=self.customer, carrier="FedEx")
        
        response = self.get_json_response(self.carriers_url)
        
        # Check response
        assert response['success'] is True
        assert "Canada Post" in response['data']
        assert "UPS" in response['data']
        assert "FedEx" in response['data']
        assert len(response['data']) == 3


class TestUSShippingAPI(APITestMixin):
    """Tests for the US shipping API endpoints."""

    def setUp(self):
        super().setUp()
        self.customer = CustomerFactory(created_by=self.user)
        self.order = OrderFactory(customer=self.customer, created_by=self.user)
        
        today = date.today()
        self.us_shipping = USShippingFactory(
            transaction=self.order,
            customer=self.customer,
            ship_to_name="US Recipient",
            ship_to_zip="12345",
            service_name="Express",
            tracking_number="US98765432",
            ship_date=today - timedelta(days=3),
            current_status="in_transit",
            delivery_status="pending"
        )
        
        self.list_url = reverse('usshipping-list')
        self.detail_url = reverse('usshipping-detail', kwargs={'pk': self.us_shipping.pk})
        self.statuses_url = reverse('usshipping-statuses')
        self.service_names_url = reverse('usshipping-service-names')

    def test_list_us_shipping(self):
        """Test retrieving a list of US shipping records."""
        # Create additional shipping records
        order2 = OrderFactory(customer=self.customer, created_by=self.user)
        order3 = OrderFactory(customer=self.customer, created_by=self.user)
        USShippingFactory(transaction=order2, customer=self.customer, service_name="Ground")
        USShippingFactory(transaction=order3, customer=self.customer, service_name="2-Day")
        
        # Get all shipping records
        response = self.get_json_response(self.list_url)
        
        # Check response
        assert response['success'] is True
        assert len(response['data']) == 3

    def test_filter_by_status(self):
        """Test filtering US shipping records by status."""
        # Create shipping records with different statuses
        order2 = OrderFactory(customer=self.customer, created_by=self.user)
        USShippingFactory(
            transaction=order2, 
            customer=self.customer, 
            current_status="delivered", 
            delivery_status="delivered"
        )
        
        # Filter by current status
        url = f"{self.list_url}?current_status=delivered"
        response = self.get_json_response(url)
        
        # Check response
        assert response['success'] is True
        assert len(response['data']) == 1
        assert response['data'][0]['current_status'] == "delivered"
        
        # Filter by delivery status
        url = f"{self.list_url}?delivery_status=delivered"
        response = self.get_json_response(url)
        
        # Check response
        assert response['success'] is True
        assert len(response['data']) == 1
        assert response['data'][0]['delivery_status'] == "delivered"

    def test_search_us_shipping(self):
        """Test searching US shipping records."""
        # Create a shipping record with searchable term
        order2 = OrderFactory(customer=self.customer, created_by=self.user)
        USShippingFactory(
            transaction=order2,
            customer=self.customer,
            tracking_number="FINDME123"
        )
        
        # Search by tracking number
        url = f"{self.list_url}?search=FINDME"
        response = self.get_json_response(url)
        
        # Check response
        assert response['success'] is True
        assert len(response['data']) == 1
        assert "FINDME" in response['data'][0]['tracking_number']

    def test_retrieve_us_shipping(self):
        """Test retrieving a single US shipping record."""
        response = self.get_json_response(self.detail_url)
        
        # Check response
        assert response['success'] is True
        assert response['data']['transaction'] == self.order.pk
        assert response['data']['customer'] == self.customer.pk
        assert response['data']['ship_to_name'] == "US Recipient"
        assert response['data']['ship_to_zip'] == "12345"
        assert response['data']['service_name'] == "Express"
        assert response['data']['current_status'] == "in_transit"

    def test_create_us_shipping(self):
        """Test creating a new US shipping record."""
        new_order = OrderFactory(customer=self.customer, created_by=self.user)
        today = date.today()
        
        data = {
            'transaction': new_order.pk,
            'customer': self.customer.pk,
            'ship_to_name': 'New US Recipient',
            'ship_to_address_1': '456 New Ave',
            'ship_to_city': 'New York',
            'ship_to_state': 'NY',
            'ship_to_zip': '10001',
            'ship_to_country_code': 'US',
            'service_name': 'Ground',
            'tracking_number': 'NEWUSTRACK456',
            'ship_date': today.isoformat(),
            'base_chg': '25.99',
            'current_status': 'pending',
            'delivery_status': 'pending'
        }
        
        response = self.get_json_response(
            self.list_url,
            method='post',
            data=data,
            status_code=status.HTTP_201_CREATED
        )
        
        # Check response
        assert response['success'] is True
        assert 'US shipping record created successfully' in response['message']
        assert response['data']['ship_to_name'] == 'New US Recipient'
        assert response['data']['tracking_number'] == 'NEWUSTRACK456'
        
        # Check calculated fields
        assert Decimal(response['data']['total_charges']) == Decimal('25.99')
        
        # Verify in database
        assert USShipping.objects.filter(transaction=new_order).exists()

    def test_update_us_shipping(self):
        """Test updating a US shipping record."""
        today = date.today()
        delivery_date = today - timedelta(days=1)
        
        data = {
            'current_status': 'delivered',
            'delivery_status': 'delivered',
            'delivery_date': delivery_date.isoformat()
        }
        
        response = self.get_json_response(
            self.detail_url,
            method='patch',
            data=data
        )
        
        # Check response
        assert response['success'] is True
        assert 'US shipping record updated successfully' in response['message']
        assert response['data']['current_status'] == 'delivered'
        assert response['data']['delivery_status'] == 'delivered'
        
        # Verify calculated delivery days
        assert response['data']['delivery_days'] == 2  # From ship_date to delivery_date
        
        # Verify in database
        self.us_shipping.refresh_from_db()
        assert self.us_shipping.current_status == 'delivered'
        assert self.us_shipping.delivery_status == 'delivered'
        assert self.us_shipping.delivery_date == delivery_date

    def test_delete_us_shipping(self):
        """Test deleting a US shipping record."""
        response = self.get_json_response(
            self.detail_url,
            method='delete'
        )
        
        # Check response
        assert response['success'] is True
        assert 'US shipping record deleted successfully' in response['message']
        
        # Verify in database
        assert not USShipping.objects.filter(pk=self.us_shipping.pk).exists()

    def test_validation_delivery_date(self):
        """Test validation for delivery date."""
        ship_date = date.today()
        delivery_date = ship_date - timedelta(days=1)  # Delivery before shipping (invalid)
        
        data = {
            'ship_date': ship_date.isoformat(),
            'delivery_date': delivery_date.isoformat()
        }
        
        response = self.get_json_response(
            self.detail_url,
            method='patch',
            data=data,
            status_code=status.HTTP_400_BAD_REQUEST
        )
        
        # Check response
        assert 'delivery_date' in response
        assert 'cannot be earlier than ship date' in response['delivery_date'][0]

    def test_get_statuses(self):
        """Test getting list of unique statuses."""
        # Create shipping with different statuses
        order2 = OrderFactory(customer=self.customer, created_by=self.user)
        USShippingFactory(
            transaction=order2,
            customer=self.customer,
            current_status='delivered',
            delivery_status='delivered'
        )
        
        response = self.get_json_response(self.statuses_url)
        
        # Check response
        assert response['success'] is True
        assert 'in_transit' in response['data']['current_statuses']
        assert 'delivered' in response['data']['current_statuses']
        assert 'pending' in response['data']['delivery_statuses']
        assert 'delivered' in response['data']['delivery_statuses']

    def test_get_service_names(self):
        """Test getting list of unique service names."""
        # Create shipping with different service names
        order2 = OrderFactory(customer=self.customer, created_by=self.user)
        USShippingFactory(
            transaction=order2,
            customer=self.customer,
            service_name='Ground'
        )
        
        response = self.get_json_response(self.service_names_url)
        
        # Check response
        assert response['success'] is True
        assert 'Express' in response['data']
        assert 'Ground' in response['data']