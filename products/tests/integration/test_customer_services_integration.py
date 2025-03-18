import pytest
from django.test import TestCase, modify_settings
from django.db.models import ProtectedError

from products.models import Product
from products.tests.factories import ProductFactory, CustomerFactory

# Try to import CustomerService, but don't fail if not available
try:
    from customer_services.models import CustomerService
    HAS_CUSTOMER_SERVICES = True
except (ImportError, ModuleNotFoundError):
    HAS_CUSTOMER_SERVICES = False


@pytest.mark.skipif(not HAS_CUSTOMER_SERVICES, reason="CustomerService app not available")
@pytest.mark.integration
class ProductCustomerServiceIntegrationTests(TestCase):
    """Tests for product integration with customer services."""
    
    @classmethod
    def setUpTestData(cls):
        """Set up test data for all tests."""
        cls.customer = CustomerFactory()
        cls.product = ProductFactory(customer=cls.customer)
        
        # Create a customer service that references this product
        if HAS_CUSTOMER_SERVICES:
            try:
                cls.customer_service = CustomerService.objects.create(
                    customer=cls.customer,
                    product=cls.product,
                    service_type="Standard",
                    price=100.00
                )
            except Exception as e:
                # Handle case where CustomerService model might have different required fields
                print(f"Could not create CustomerService: {str(e)}")
    
    def test_product_has_customer_service(self):
        """Test that a product can have customer services."""
        if not HAS_CUSTOMER_SERVICES:
            self.skipTest("CustomerService app not available")
        
        # Verify the product has the expected customer service
        self.assertTrue(hasattr(self.product, 'customerservice_set'))
        self.assertEqual(self.product.customerservice_set.count(), 1)
    
    def test_customer_service_references_product(self):
        """Test that a customer service correctly references a product."""
        if not HAS_CUSTOMER_SERVICES:
            self.skipTest("CustomerService app not available")
        
        # Verify the customer service has the correct product
        self.assertEqual(self.customer_service.product, self.product)
    
    def test_product_delete_protection(self):
        """Test that a product with customer services cannot be deleted."""
        if not HAS_CUSTOMER_SERVICES:
            self.skipTest("CustomerService app not available")
        
        # Attempt to delete the product that has a customer service
        # This should be prevented by the destroy method in ProductViewSet
        # or by a database constraint if using PROTECT
        try:
            with self.assertRaises(ProtectedError):
                self.product.delete()
                
            # Verify the product still exists
            self.assertTrue(Product.objects.filter(id=self.product.id).exists())
        except AssertionError:
            # If no ProtectedError was raised, the view's custom check should have prevented deletion
            # We can verify this by checking if the product was actually deleted
            self.assertTrue(Product.objects.filter(id=self.product.id).exists())
    
    def test_update_product_reflected_in_customer_service(self):
        """Test that updating a product is reflected in customer services."""
        if not HAS_CUSTOMER_SERVICES:
            self.skipTest("CustomerService app not available")
        
        # Update the product
        new_sku = "UPDATED-SKU"
        self.product.sku = new_sku
        self.product.save()
        
        # Refresh customer service from database
        self.customer_service.refresh_from_db()
        
        # The customer service should reference the updated product
        self.assertEqual(self.customer_service.product.sku, new_sku)
    
    def test_customer_service_creation_for_product(self):
        """Test creating a customer service for a product."""
        if not HAS_CUSTOMER_SERVICES:
            self.skipTest("CustomerService app not available")
        
        # Create a new product
        new_product = ProductFactory(customer=self.customer)
        
        # Create a customer service for this product
        new_service = CustomerService.objects.create(
            customer=self.customer,
            product=new_product,
            service_type="Premium",
            price=150.00
        )
        
        # Verify the relationship is correct
        self.assertEqual(new_service.product, new_product)
        self.assertTrue(new_product.customerservice_set.filter(id=new_service.id).exists())
    
    def test_customer_service_delete_without_affecting_product(self):
        """Test that deleting a customer service doesn't affect the product."""
        if not HAS_CUSTOMER_SERVICES:
            self.skipTest("CustomerService app not available")
        
        # Store product ID for verification
        product_id = self.product.id
        
        # Delete the customer service
        self.customer_service.delete()
        
        # Verify the product still exists
        self.assertTrue(Product.objects.filter(id=product_id).exists())
        
        # Verify the customer service was deleted
        self.assertEqual(self.product.customerservice_set.count(), 0)