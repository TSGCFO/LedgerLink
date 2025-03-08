import pytest
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from products.serializers import ProductSerializer
from .factories import ProductFactory, CustomerFactory


@pytest.mark.db
class TestProductSerializer:
    """Test suite for the ProductSerializer."""

    def test_serialization(self, db):
        """Test serializing a Product instance."""
        product = ProductFactory()
        serializer = ProductSerializer(product)
        data = serializer.data
        
        # Check all fields are present
        assert 'id' in data
        assert 'sku' in data
        assert 'customer' in data
        assert 'customer_details' in data
        assert 'labeling_unit_1' in data
        assert 'labeling_quantity_1' in data
        assert 'created_at' in data
        assert 'updated_at' in data
        
        # Check customer_details
        assert data['customer_details']['id'] == product.customer.id
        assert data['customer_details']['company_name'] == product.customer.company_name
        
        # Check values match
        assert data['sku'] == product.sku
        assert data['customer'] == product.customer.id
        assert data['labeling_unit_1'] == product.labeling_unit_1
        assert data['labeling_quantity_1'] == product.labeling_quantity_1

    def test_deserialization(self, db):
        """Test deserializing data to create a Product."""
        customer = CustomerFactory()
        data = {
            'sku': 'NEW-SKU-001',
            'customer': customer.id,
            'labeling_unit_1': 'BOX',
            'labeling_quantity_1': 5,
            'labeling_unit_2': 'INNER',
            'labeling_quantity_2': 10
        }
        
        serializer = ProductSerializer(data=data)
        assert serializer.is_valid()
        
        product = serializer.save()
        assert product.sku == 'NEW-SKU-001'
        assert product.customer == customer
        assert product.labeling_unit_1 == 'BOX'
        assert product.labeling_quantity_1 == 5
        assert product.labeling_unit_2 == 'INNER'
        assert product.labeling_quantity_2 == 10

    def test_update(self, db):
        """Test updating a Product via serializer."""
        product = ProductFactory(
            sku='OLD-SKU',
            labeling_unit_1='CASE',
            labeling_quantity_1=20
        )
        
        data = {
            'sku': 'UPDATED-SKU',
            'customer': product.customer.id,
            'labeling_unit_1': 'PALLET',
            'labeling_quantity_1': 25
        }
        
        serializer = ProductSerializer(product, data=data, partial=True)
        assert serializer.is_valid()
        
        updated_product = serializer.save()
        assert updated_product.sku == 'UPDATED-SKU'
        assert updated_product.labeling_unit_1 == 'PALLET'
        assert updated_product.labeling_quantity_1 == 25

    def test_sku_uppercase_conversion(self, db):
        """Test that SKUs are converted to uppercase."""
        customer = CustomerFactory()
        data = {
            'sku': 'lowercase-sku',
            'customer': customer.id,
            'labeling_unit_1': 'BOX',
            'labeling_quantity_1': 5
        }
        
        serializer = ProductSerializer(data=data)
        assert serializer.is_valid()
        
        product = serializer.save()
        assert product.sku == 'LOWERCASE-SKU'

    def test_sku_uniqueness_validation(self, db):
        """Test validation for unique SKU per customer."""
        customer = CustomerFactory()
        
        # Create a product with a specific SKU
        ProductFactory(
            customer=customer,
            sku='EXISTING-SKU'
        )
        
        # Attempt to create another product with the same SKU for the same customer
        data = {
            'sku': 'EXISTING-SKU',
            'customer': customer.id,
            'labeling_unit_1': 'BOX',
            'labeling_quantity_1': 5
        }
        
        serializer = ProductSerializer(data=data)
        assert not serializer.is_valid()
        assert 'sku' in serializer.errors
        assert "This SKU is already in use for this customer" in str(serializer.errors['sku'])

    def test_negative_quantity_validation(self, db):
        """Test validation for negative quantities."""
        customer = CustomerFactory()
        
        data = {
            'sku': 'NEGATIVE-QTY',
            'customer': customer.id,
            'labeling_unit_1': 'BOX',
            'labeling_quantity_1': -5  # Negative quantity
        }
        
        serializer = ProductSerializer(data=data)
        assert not serializer.is_valid()
        assert 'labeling_quantity_1' in serializer.errors
        assert "Quantity cannot be negative" in str(serializer.errors['labeling_quantity_1'])