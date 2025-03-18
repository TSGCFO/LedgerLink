import pytest
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.db import transaction
from products.models import Product
from .factories import ProductFactory, CustomerFactory


@pytest.mark.db
class TestProductModel:
    """Test suite for the Product model."""

    def test_product_creation(self, db):
        """Test basic product creation."""
        product = ProductFactory()
        assert product.id is not None
        assert product.sku is not None
        assert product.customer is not None
        assert product.created_at is not None
        assert product.updated_at is not None

    def test_str_representation(self, db):
        """Test string representation of Product."""
        customer = CustomerFactory(company_name="Test Company")
        product = ProductFactory(customer=customer, sku="TEST-SKU")
        assert str(product) == "Test Company - TEST-SKU"

    def test_unique_constraint(self, db):
        """Test the unique constraint on sku and customer."""
        customer = CustomerFactory()
        ProductFactory(customer=customer, sku="UNIQUE-SKU")
        
        # Creating another product with the same SKU for the same customer should fail
        with pytest.raises(IntegrityError), transaction.atomic():
            ProductFactory(customer=customer, sku="UNIQUE-SKU")
        
        # Creating a product with the same SKU for a different customer should succeed
        different_customer = CustomerFactory()
        product = ProductFactory(customer=different_customer, sku="UNIQUE-SKU")
        assert product.id is not None

    def test_check_constraints(self, db):
        """Test check constraints for quantities."""
        # Test negative quantity validation
        with pytest.raises(IntegrityError), transaction.atomic():
            ProductFactory(labeling_quantity_1=-1)
        
        with pytest.raises(IntegrityError), transaction.atomic():
            ProductFactory(labeling_quantity_2=-5)
            
        with pytest.raises(IntegrityError), transaction.atomic():
            ProductFactory(labeling_quantity_3=-10)
            
        with pytest.raises(IntegrityError), transaction.atomic():
            ProductFactory(labeling_quantity_4=-15)
            
        with pytest.raises(IntegrityError), transaction.atomic():
            ProductFactory(labeling_quantity_5=-20)
    
    def test_null_and_blank_fields(self, db):
        """Test that null and blank fields are handled correctly."""
        # All optional fields set to None
        product = ProductFactory(
            labeling_unit_2=None, labeling_quantity_2=None,
            labeling_unit_3=None, labeling_quantity_3=None,
            labeling_unit_4=None, labeling_quantity_4=None,
            labeling_unit_5=None, labeling_quantity_5=None
        )
        assert product.id is not None
        
        # When retrieving, the values should still be None
        retrieved_product = Product.objects.get(id=product.id)
        assert retrieved_product.labeling_unit_2 is None
        assert retrieved_product.labeling_quantity_2 is None
        assert retrieved_product.labeling_unit_3 is None
        assert retrieved_product.labeling_quantity_3 is None
        assert retrieved_product.labeling_unit_4 is None
        assert retrieved_product.labeling_quantity_4 is None
        assert retrieved_product.labeling_unit_5 is None
        assert retrieved_product.labeling_quantity_5 is None