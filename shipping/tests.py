from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth.models import User
from decimal import Decimal
from datetime import date, datetime, timedelta
from django.utils import timezone

from .models import CADShipping, USShipping
from .serializers import CADShippingSerializer, USShippingSerializer
from orders.models import Order
from customers.models import Customer


class CADShippingModelTests(TestCase):
    """Test cases for the CADShipping model"""

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
            reference_number="REF-CAD-001",
            ship_to_name="Canadian Recipient",
            ship_to_address="123 Maple St",
            ship_to_city="Toronto",
            ship_to_state="ON",
            ship_to_zip="M5V 2N4"
        )

    def test_create_cad_shipping(self):
        """Test creating a CADShipping instance"""
        cad_shipping = CADShipping.objects.create(
            transaction=self.order,
            customer=self.customer,
            service_code_description="Priority",
            ship_to_name="Canadian Recipient",
            ship_to_address_1="123 Maple St",
            ship_to_city="Toronto",
            ship_to_state="ON",
            ship_to_postal_code="M5V 2N4",
            pre_tax_shipping_charge=Decimal("25.00"),
            tax1type="HST",
            tax1amount=Decimal("3.25"),
            carrier="Canada Post"
        )
        
        self.assertEqual(cad_shipping.transaction, self.order)
        self.assertEqual(cad_shipping.customer, self.customer)
        self.assertEqual(cad_shipping.ship_to_name, "Canadian Recipient")
        self.assertEqual(cad_shipping.carrier, "Canada Post")
        self.assertEqual(cad_shipping.pre_tax_shipping_charge, Decimal("25.00"))
        self.assertEqual(cad_shipping.tax1amount, Decimal("3.25"))

    def test_cad_shipping_str_representation(self):
        """Test the string representation of a CADShipping"""
        cad_shipping = CADShipping.objects.create(
            transaction=self.order,
            customer=self.customer,
            carrier="Canada Post"
        )
        self.assertEqual(str(cad_shipping), f"CAD Shipping for Order {self.order.transaction_id}")

    def test_cad_shipping_cascade_delete_from_order(self):
        """Test that CADShipping is deleted when Order is deleted"""
        CADShipping.objects.create(
            transaction=self.order,
            customer=self.customer
        )
        
        # Verify shipping record exists
        self.assertEqual(CADShipping.objects.count(), 1)
        
        # Delete the order
        self.order.delete()
        
        # Verify shipping record is deleted via cascade
        self.assertEqual(CADShipping.objects.count(), 0)


class USShippingModelTests(TestCase):
    """Test cases for the USShipping model"""

    def setUp(self):
        """Set up test data"""
        self.customer = Customer.objects.create(
            company_name="Test Company",
            contact_name="John Doe",
            contact_email="john@example.com",
            contact_phone="123-456-7890"
        )
        
        self.order = Order.objects.create(
            transaction_id=54321,
            customer=self.customer,
            reference_number="REF-US-001",
            ship_to_name="US Recipient",
            ship_to_address="456 Main St",
            ship_to_city="New York",
            ship_to_state="NY",
            ship_to_zip="10001"
        )

    def test_create_us_shipping(self):
        """Test creating a USShipping instance"""
        ship_date = date.today()
        us_shipping = USShipping.objects.create(
            transaction=self.order,
            customer=self.customer,
            ship_date=ship_date,
            ship_to_name="US Recipient",
            ship_to_address_1="456 Main St",
            ship_to_city="New York",
            ship_to_state="NY",
            ship_to_zip="10001",
            service_name="Express",
            weight_lbs=Decimal("5.5"),
            base_chg=Decimal("15.99"),
            current_status="In Transit",
            delivery_status="Pending"
        )
        
        self.assertEqual(us_shipping.transaction, self.order)
        self.assertEqual(us_shipping.customer, self.customer)
        self.assertEqual(us_shipping.ship_to_name, "US Recipient")
        self.assertEqual(us_shipping.service_name, "Express")
        self.assertEqual(us_shipping.base_chg, Decimal("15.99"))
        self.assertEqual(us_shipping.ship_date, ship_date)
        self.assertEqual(us_shipping.current_status, "In Transit")

    def test_us_shipping_str_representation(self):
        """Test the string representation of a USShipping"""
        us_shipping = USShipping.objects.create(
            transaction=self.order,
            customer=self.customer,
            service_name="Express"
        )
        self.assertEqual(str(us_shipping), f"US Shipping for Order {self.order.transaction_id}")

    def test_us_shipping_cascade_delete_from_order(self):
        """Test that USShipping is deleted when Order is deleted"""
        USShipping.objects.create(
            transaction=self.order,
            customer=self.customer
        )
        
        # Verify shipping record exists
        self.assertEqual(USShipping.objects.count(), 1)
        
        # Delete the order
        self.order.delete()
        
        # Verify shipping record is deleted via cascade
        self.assertEqual(USShipping.objects.count(), 0)

    def test_us_shipping_delivery_date_calculation(self):
        """Test delivery date calculation fields"""
        ship_date = date.today()
        delivery_date = ship_date + timedelta(days=3)
        us_shipping = USShipping.objects.create(
            transaction=self.order,
            customer=self.customer,
            ship_date=ship_date,
            delivery_date=delivery_date,
            days_to_first_deliver=3
        )
        
        self.assertEqual(us_shipping.days_to_first_deliver, 3)


class CADShippingSerializerTests(TestCase):
    """Test cases for the CADShippingSerializer"""

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
            reference_number="REF-CAD-001",
            ship_to_name="Canadian Recipient",
            ship_to_address="123 Maple St",
            ship_to_city="Toronto",
            ship_to_state="ON",
            ship_to_zip="M5V 2N4"
        )
        
        self.cad_shipping = CADShipping.objects.create(
            transaction=self.order,
            customer=self.customer,
            service_code_description="Priority",
            ship_to_name="Canadian Recipient",
            ship_to_address_1="123 Maple St",
            ship_to_city="Toronto",
            ship_to_state="ON",
            ship_to_postal_code="M5V 2N4",
            pre_tax_shipping_charge=Decimal("25.00"),
            tax1type="HST",
            tax1amount=Decimal("3.25"),
            tax2type="GST",
            tax2amount=Decimal("1.25"),
            fuel_surcharge=Decimal("1.50"),
            carrier="Canada Post"
        )
        
        self.serializer = CADShippingSerializer(instance=self.cad_shipping)

    def test_cad_shipping_serializer_contains_expected_fields(self):
        """Test serializer contains expected fields"""
        data = self.serializer.data
        
        expected_fields = [
            'transaction', 'order_details', 'customer', 'customer_details',
            'service_code_description', 'ship_to_name', 'ship_to_address_1',
            'ship_to_city', 'ship_to_state', 'ship_to_postal_code',
            'tracking_number', 'pre_tax_shipping_charge', 'tax1type',
            'tax1amount', 'tax2type', 'tax2amount', 'fuel_surcharge',
            'carrier', 'total_tax', 'total_charges'
        ]
        
        for field in expected_fields:
            self.assertIn(field, data)

    def test_cad_shipping_total_tax_calculation(self):
        """Test total tax calculation"""
        data = self.serializer.data
        
        # Total tax should be the sum of all tax amounts
        expected_total_tax = Decimal("3.25") + Decimal("1.25")
        self.assertEqual(Decimal(data['total_tax']), expected_total_tax)
        
    def test_cad_shipping_total_charges_calculation(self):
        """Test total charges calculation"""
        data = self.serializer.data
        
        # Total charges should be pre_tax_shipping_charge + fuel_surcharge + total_tax
        expected_total_charges = Decimal("25.00") + Decimal("1.50") + Decimal("4.50")
        self.assertEqual(Decimal(data['total_charges']), expected_total_charges)

    def test_cad_shipping_serializer_validation(self):
        """Test validation of shipping address fields"""
        # When some shipping fields are provided, all required fields must be present
        incomplete_data = {
            'customer': self.customer.id,
            'ship_to_name': 'Test Recipient',
            'ship_to_address_1': '123 Test St'
            # Missing city, state, and postal code
        }
        
        serializer = CADShippingSerializer(data=incomplete_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('shipping', serializer.errors)
        
        # When all required fields are provided, validation should pass
        complete_data = {
            'customer': self.customer.id,
            'ship_to_name': 'Test Recipient',
            'ship_to_address_1': '123 Test St',
            'ship_to_city': 'Test City',
            'ship_to_state': 'TS',
            'ship_to_postal_code': 'T1T 1T1'
        }
        
        serializer = CADShippingSerializer(data=complete_data)
        self.assertTrue(serializer.is_valid())


class USShippingSerializerTests(TestCase):
    """Test cases for the USShippingSerializer"""

    def setUp(self):
        """Set up test data"""
        self.customer = Customer.objects.create(
            company_name="Test Company",
            contact_name="John Doe",
            contact_email="john@example.com",
            contact_phone="123-456-7890"
        )
        
        self.order = Order.objects.create(
            transaction_id=54321,
            customer=self.customer,
            reference_number="REF-US-001",
            ship_to_name="US Recipient",
            ship_to_address="456 Main St",
            ship_to_city="New York",
            ship_to_state="NY",
            ship_to_zip="10001"
        )
        
        ship_date = date.today()
        delivery_date = ship_date + timedelta(days=3)
        self.us_shipping = USShipping.objects.create(
            transaction=self.order,
            customer=self.customer,
            ship_date=ship_date,
            ship_to_name="US Recipient",
            ship_to_address_1="456 Main St",
            ship_to_city="New York",
            ship_to_state="NY",
            ship_to_zip="10001",
            service_name="Express",
            base_chg=Decimal("15.99"),
            carrier_peak_charge=Decimal("2.50"),
            accessorial_charges=Decimal("1.00"),
            hst=Decimal("1.75"),
            delivery_date=delivery_date,
            current_status="In Transit",
            delivery_status="Pending"
        )
        
        self.serializer = USShippingSerializer(instance=self.us_shipping)

    def test_us_shipping_serializer_contains_expected_fields(self):
        """Test serializer contains expected fields"""
        data = self.serializer.data
        
        expected_fields = [
            'transaction', 'order_details', 'customer', 'customer_details',
            'ship_date', 'ship_to_name', 'ship_to_address_1',
            'ship_to_city', 'ship_to_state', 'ship_to_zip',
            'service_name', 'base_chg', 'carrier_peak_charge',
            'accessorial_charges', 'hst', 'current_status',
            'delivery_status', 'delivery_date', 'total_charges',
            'delivery_days'
        ]
        
        for field in expected_fields:
            self.assertIn(field, data)

    def test_us_shipping_total_charges_calculation(self):
        """Test total charges calculation"""
        data = self.serializer.data
        
        # Total charges should include base_chg, carrier_peak_charge, accessorial_charges, and hst
        expected_total_charges = Decimal("15.99") + Decimal("2.50") + Decimal("1.00") + Decimal("1.75")
        self.assertEqual(Decimal(data['total_charges']), expected_total_charges)

    def test_us_shipping_delivery_days_calculation(self):
        """Test delivery days calculation"""
        data = self.serializer.data
        
        # Delivery days should be calculated from ship_date and delivery_date
        expected_days = 3
        self.assertEqual(data['delivery_days'], expected_days)
        
        # When days_to_first_deliver is explicitly set, it should be returned
        self.us_shipping.days_to_first_deliver = 4
        self.us_shipping.save()
        serializer = USShippingSerializer(instance=self.us_shipping)
        self.assertEqual(serializer.data['delivery_days'], 4)
        
    def test_us_shipping_serializer_validation(self):
        """Test validation logic"""
        # Test shipping address validation
        incomplete_data = {
            'customer': self.customer.id,
            'ship_to_name': 'Test Recipient',
            # Missing required shipping fields
        }
        
        serializer = USShippingSerializer(data=incomplete_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('shipping', serializer.errors)
        
        # Test date validation: delivery_date before ship_date
        ship_date = date.today()
        invalid_data = {
            'customer': self.customer.id,
            'ship_to_name': 'Test Recipient',
            'ship_to_address_1': '123 Main St',
            'ship_to_city': 'Test City',
            'ship_to_state': 'TS',
            'ship_to_zip': '12345',
            'ship_date': ship_date,
            'delivery_date': ship_date - timedelta(days=1)  # Invalid: before ship_date
        }
        
        serializer = USShippingSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('delivery_date', serializer.errors)
        
        # Test date validation: first_attempt_date before ship_date
        invalid_data = {
            'customer': self.customer.id,
            'ship_to_name': 'Test Recipient',
            'ship_to_address_1': '123 Main St',
            'ship_to_city': 'Test City',
            'ship_to_state': 'TS',
            'ship_to_zip': '12345',
            'ship_date': ship_date,
            'first_attempt_date': ship_date - timedelta(days=1)  # Invalid: before ship_date
        }
        
        serializer = USShippingSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('first_attempt_date', serializer.errors)


class CADShippingAPITests(APITestCase):
    """Test cases for the CADShipping API endpoints"""

    def setUp(self):
        """Set up test data and authenticate"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        # Create test data
        self.customer = Customer.objects.create(
            company_name="Test Company",
            contact_name="John Doe",
            contact_email="john@example.com",
            contact_phone="123-456-7890"
        )
        
        self.order = Order.objects.create(
            transaction_id=12345,
            customer=self.customer,
            reference_number="REF-CAD-001",
            ship_to_name="Canadian Recipient",
            ship_to_address="123 Maple St",
            ship_to_city="Toronto",
            ship_to_state="ON",
            ship_to_zip="M5V 2N4"
        )
        
        self.shipping = CADShipping.objects.create(
            transaction=self.order,
            customer=self.customer,
            service_code_description="Priority",
            ship_to_name="Canadian Recipient",
            ship_to_address_1="123 Maple St",
            ship_to_city="Toronto",
            ship_to_state="ON",
            ship_to_postal_code="M5V 2N4",
            pre_tax_shipping_charge=Decimal("25.00"),
            tax1type="HST",
            tax1amount=Decimal("3.25"),
            carrier="Canada Post",
            ship_date=timezone.now()
        )
        
        # Create another shipping record for testing filtering
        self.another_customer = Customer.objects.create(
            company_name="Another Company",
            contact_name="Jane Smith",
            contact_email="jane@example.com",
            contact_phone="987-654-3210"
        )
        
        self.another_order = Order.objects.create(
            transaction_id=67890,
            customer=self.another_customer,
            reference_number="REF-CAD-002",
            ship_to_name="Another Recipient",
            ship_to_address="456 Elm St",
            ship_to_city="Vancouver",
            ship_to_state="BC",
            ship_to_zip="V6B 2Z4"
        )
        
        self.another_shipping = CADShipping.objects.create(
            transaction=self.another_order,
            customer=self.another_customer,
            service_code_description="Standard",
            ship_to_name="Another Recipient",
            ship_to_address_1="456 Elm St",
            ship_to_city="Vancouver",
            ship_to_state="BC",
            ship_to_postal_code="V6B 2Z4",
            pre_tax_shipping_charge=Decimal("18.75"),
            carrier="Purolator",
            ship_date=timezone.now() - timedelta(days=5)
        )
        
        # URLs for API endpoints
        self.list_url = reverse('cadshipping-list')
        self.detail_url = reverse('cadshipping-detail', kwargs={'pk': self.shipping.pk})
        self.carriers_url = reverse('cadshipping-carriers')

    def test_get_cad_shipping_list(self):
        """Test GET request to retrieve all CAD shipping records"""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(len(response.data['data']), 2)
        
    def test_filter_by_customer(self):
        """Test filtering shipping records by customer"""
        url = f"{self.list_url}?customer={self.customer.id}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['transaction'], self.order.id)
        
    def test_filter_by_carrier(self):
        """Test filtering shipping records by carrier"""
        url = f"{self.list_url}?carrier=Canada Post"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['carrier'], "Canada Post")
        
    def test_search_functionality(self):
        """Test searching shipping records"""
        # Search by name
        url = f"{self.list_url}?search=Canadian"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['ship_to_name'], "Canadian Recipient")
        
    def test_get_cad_shipping_detail(self):
        """Test retrieving a specific CAD shipping record"""
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['transaction'], self.order.id)
        self.assertEqual(response.data['carrier'], "Canada Post")
        
    def test_create_cad_shipping(self):
        """Test creating a new CAD shipping record"""
        new_order = Order.objects.create(
            transaction_id=13579,
            customer=self.customer,
            reference_number="REF-CAD-003",
            ship_to_name="New Recipient",
            ship_to_address="789 Oak St",
            ship_to_city="Montreal",
            ship_to_state="QC",
            ship_to_zip="H2Y 1C6"
        )
        
        data = {
            'transaction': new_order.id,
            'customer': self.customer.id,
            'ship_to_name': 'New Recipient',
            'ship_to_address_1': '789 Oak St',
            'ship_to_city': 'Montreal',
            'ship_to_state': 'QC',
            'ship_to_postal_code': 'H2Y 1C6',
            'carrier': 'UPS',
            'pre_tax_shipping_charge': '22.50'
        }
        
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        
        # Verify record was created
        self.assertEqual(CADShipping.objects.count(), 3)
        
    def test_update_cad_shipping(self):
        """Test updating a CAD shipping record"""
        data = {
            'carrier': 'Updated Carrier',
            'pre_tax_shipping_charge': '30.00',
            'customer': self.customer.id
        }
        
        response = self.client.patch(self.detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        # Verify record was updated
        self.shipping.refresh_from_db()
        self.assertEqual(self.shipping.carrier, 'Updated Carrier')
        self.assertEqual(self.shipping.pre_tax_shipping_charge, Decimal('30.00'))
        
    def test_delete_cad_shipping(self):
        """Test deleting a CAD shipping record"""
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        # Verify record was deleted
        self.assertEqual(CADShipping.objects.count(), 1)
        
    def test_carriers_action(self):
        """Test the carriers custom action"""
        response = self.client.get(self.carriers_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        # Should return list of unique carriers
        carriers = response.data['data']
        self.assertIsInstance(carriers, list)
        self.assertEqual(len(carriers), 2)
        self.assertIn('Canada Post', carriers)
        self.assertIn('Purolator', carriers)
        
    def test_unauthorized_access(self):
        """Test unauthorized access to the API"""
        self.client.logout()
        
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class USShippingAPITests(APITestCase):
    """Test cases for the USShipping API endpoints"""

    def setUp(self):
        """Set up test data and authenticate"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        # Create test data
        self.customer = Customer.objects.create(
            company_name="Test Company",
            contact_name="John Doe",
            contact_email="john@example.com",
            contact_phone="123-456-7890"
        )
        
        self.order = Order.objects.create(
            transaction_id=54321,
            customer=self.customer,
            reference_number="REF-US-001",
            ship_to_name="US Recipient",
            ship_to_address="123 Main St",
            ship_to_city="New York",
            ship_to_state="NY",
            ship_to_zip="10001"
        )
        
        self.shipping = USShipping.objects.create(
            transaction=self.order,
            customer=self.customer,
            ship_date=date.today(),
            ship_to_name="US Recipient",
            ship_to_address_1="123 Main St",
            ship_to_city="New York",
            ship_to_state="NY",
            ship_to_zip="10001",
            service_name="Express",
            base_chg=Decimal("15.99"),
            current_status="In Transit",
            delivery_status="Pending"
        )
        
        # Create another shipping record for testing filtering
        self.another_customer = Customer.objects.create(
            company_name="Another Company",
            contact_name="Jane Smith",
            contact_email="jane@example.com",
            contact_phone="987-654-3210"
        )
        
        self.another_order = Order.objects.create(
            transaction_id=98765,
            customer=self.another_customer,
            reference_number="REF-US-002",
            ship_to_name="Another Recipient",
            ship_to_address="456 Broadway",
            ship_to_city="Los Angeles",
            ship_to_state="CA",
            ship_to_zip="90001"
        )
        
        self.another_shipping = USShipping.objects.create(
            transaction=self.another_order,
            customer=self.another_customer,
            ship_date=date.today() - timedelta(days=7),
            ship_to_name="Another Recipient",
            ship_to_address_1="456 Broadway",
            ship_to_city="Los Angeles",
            ship_to_state="CA",
            ship_to_zip="90001",
            service_name="Ground",
            base_chg=Decimal("9.99"),
            current_status="Delivered",
            delivery_status="Delivered"
        )
        
        # URLs for API endpoints
        self.list_url = reverse('usshipping-list')
        self.detail_url = reverse('usshipping-detail', kwargs={'pk': self.shipping.pk})
        self.statuses_url = reverse('usshipping-statuses')
        self.service_names_url = reverse('usshipping-service-names')

    def test_get_us_shipping_list(self):
        """Test GET request to retrieve all US shipping records"""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(len(response.data['data']), 2)
        
    def test_filter_by_customer(self):
        """Test filtering shipping records by customer"""
        url = f"{self.list_url}?customer={self.customer.id}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['transaction'], self.order.id)
        
    def test_filter_by_status(self):
        """Test filtering shipping records by status"""
        url = f"{self.list_url}?current_status=Delivered"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['current_status'], "Delivered")
        
        url = f"{self.list_url}?delivery_status=Pending"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['delivery_status'], "Pending")
        
    def test_search_functionality(self):
        """Test searching shipping records"""
        # Search by service name
        url = f"{self.list_url}?search=Express"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['service_name'], "Express")
        
    def test_get_us_shipping_detail(self):
        """Test retrieving a specific US shipping record"""
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['transaction'], self.order.id)
        self.assertEqual(response.data['service_name'], "Express")
        
    def test_create_us_shipping(self):
        """Test creating a new US shipping record"""
        new_order = Order.objects.create(
            transaction_id=24680,
            customer=self.customer,
            reference_number="REF-US-003",
            ship_to_name="New Recipient",
            ship_to_address="789 Third St",
            ship_to_city="Chicago",
            ship_to_state="IL",
            ship_to_zip="60601"
        )
        
        data = {
            'transaction': new_order.id,
            'customer': self.customer.id,
            'ship_date': '2025-03-01',
            'ship_to_name': 'New Recipient',
            'ship_to_address_1': '789 Third St',
            'ship_to_city': 'Chicago',
            'ship_to_state': 'IL',
            'ship_to_zip': '60601',
            'service_name': 'Priority',
            'current_status': 'Pending'
        }
        
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        
        # Verify record was created
        self.assertEqual(USShipping.objects.count(), 3)
        
    def test_update_us_shipping(self):
        """Test updating a US shipping record"""
        data = {
            'service_name': 'Updated Service',
            'current_status': 'Delivered',
            'customer': self.customer.id
        }
        
        response = self.client.patch(self.detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        # Verify record was updated
        self.shipping.refresh_from_db()
        self.assertEqual(self.shipping.service_name, 'Updated Service')
        self.assertEqual(self.shipping.current_status, 'Delivered')
        
    def test_delete_us_shipping(self):
        """Test deleting a US shipping record"""
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        # Verify record was deleted
        self.assertEqual(USShipping.objects.count(), 1)
        
    def test_statuses_action(self):
        """Test the statuses custom action"""
        response = self.client.get(self.statuses_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        # Should return separate lists for current and delivery statuses
        self.assertIn('current_statuses', response.data['data'])
        self.assertIn('delivery_statuses', response.data['data'])
        
        current_statuses = response.data['data']['current_statuses']
        delivery_statuses = response.data['data']['delivery_statuses']
        
        self.assertIn('In Transit', current_statuses)
        self.assertIn('Delivered', current_statuses)
        self.assertIn('Pending', delivery_statuses)
        self.assertIn('Delivered', delivery_statuses)
        
    def test_service_names_action(self):
        """Test the service_names custom action"""
        response = self.client.get(self.service_names_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        # Should return list of unique service names
        service_names = response.data['data']
        self.assertIsInstance(service_names, list)
        self.assertEqual(len(service_names), 2)
        self.assertIn('Express', service_names)
        self.assertIn('Ground', service_names)
        
    def test_unauthorized_access(self):
        """Test unauthorized access to the API"""
        self.client.logout()
        
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
