import os
import json
import logging
from pact import Verifier
from django.test import TestCase
from django.conf import settings
from decimal import Decimal
from materials.models import Material, BoxPrice
from materials.tests.factories import MaterialFactory, BoxPriceFactory


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MaterialPactProviderTest(TestCase):
    """
    Test that the Material API can satisfy the contract
    defined by the frontend consumer.
    """
    
    def setUp(self):
        """Set up test data and pact verifier."""
        # Create test materials
        self.material1 = MaterialFactory(
            id=1,  # Explicitly set ID for deterministic tests
            name='Test Material 1',
            description='First test material',
            unit_price=Decimal('10.50')
        )
        
        self.material2 = MaterialFactory(
            id=2,  # Explicitly set ID for deterministic tests
            name='Test Material 2',
            description='Second test material',
            unit_price=Decimal('15.75')
        )
        
        # Pact setup
        self.pact_dir = os.path.join(settings.BASE_DIR, 'frontend', 'pact', 'pacts')
        self.pact_uri = f"http://{settings.ALLOWED_HOSTS[0] if settings.ALLOWED_HOSTS else 'localhost'}:8000"
        self.provider_name = 'ledgerlink-materials-provider'
        self.consumer_name = 'ledgerlink-materials-consumer'
        
        # Verifier setup
        self.verifier = Verifier(
            provider="ledgerlink-materials-provider",
            provider_base_url=self.pact_uri
        )
    
    def test_materials_contract(self):
        """Test that the API satisfies the materials contract."""
        pact_file = os.path.join(self.pact_dir, f"{self.consumer_name}-{self.provider_name}.json")
        
        # Check if pact file exists
        if not os.path.exists(pact_file):
            logger.warning(f"Pact file {pact_file} does not exist. Skipping test.")
            return
        
        # Define state handlers for provider states
        provider_states = {
            "materials exist": self._materials_exist,
            "no materials exist": self._no_materials_exist,
            "a specific material exists": self._specific_material_exists
        }
        
        # Verify the contract
        success, logs = self.verifier.verify_pacts(
            pact_files=[pact_file],
            provider_states_setup_url=f"{self.pact_uri}/pact-provider-state",
            provider_states=provider_states,
            verbose=True
        )
        
        # Log results
        for log in logs:
            logger.info(log)
        
        # Assert that verification was successful
        self.assertTrue(success)
    
    def _materials_exist(self, provider_state):
        """Set up state where materials exist."""
        # Materials are already created in setUp
        return True
    
    def _no_materials_exist(self, provider_state):
        """Set up state where no materials exist."""
        Material.objects.all().delete()
        return True
    
    def _specific_material_exists(self, provider_state):
        """Set up state where a specific material exists."""
        # Recreate material with id=1 if it doesn't exist
        Material.objects.filter(id=1).delete()
        MaterialFactory(
            id=1,
            name='Specific Material',
            description='Material for specific test',
            unit_price=Decimal('12.34')
        )
        return True


class BoxPricePactProviderTest(TestCase):
    """
    Test that the BoxPrice API can satisfy the contract
    defined by the frontend consumer.
    """
    
    def setUp(self):
        """Set up test data and pact verifier."""
        # Create test box prices
        self.box_price1 = BoxPriceFactory(
            id=1,  # Explicitly set ID for deterministic tests
            box_type='Small Box',
            price=Decimal('5.25'),
            length=Decimal('5.00'),
            width=Decimal('4.00'),
            height=Decimal('3.00')
        )
        
        self.box_price2 = BoxPriceFactory(
            id=2,  # Explicitly set ID for deterministic tests
            box_type='Medium Box',
            price=Decimal('8.50'),
            length=Decimal('10.00'),
            width=Decimal('8.00'),
            height=Decimal('6.00')
        )
        
        # Pact setup
        self.pact_dir = os.path.join(settings.BASE_DIR, 'frontend', 'pact', 'pacts')
        self.pact_uri = f"http://{settings.ALLOWED_HOSTS[0] if settings.ALLOWED_HOSTS else 'localhost'}:8000"
        self.provider_name = 'ledgerlink-boxprices-provider'
        self.consumer_name = 'ledgerlink-boxprices-consumer'
        
        # Verifier setup
        self.verifier = Verifier(
            provider="ledgerlink-boxprices-provider",
            provider_base_url=self.pact_uri
        )
    
    def test_box_prices_contract(self):
        """Test that the API satisfies the box prices contract."""
        pact_file = os.path.join(self.pact_dir, f"{self.consumer_name}-{self.provider_name}.json")
        
        # Check if pact file exists
        if not os.path.exists(pact_file):
            logger.warning(f"Pact file {pact_file} does not exist. Skipping test.")
            return
        
        # Define state handlers for provider states
        provider_states = {
            "box prices exist": self._box_prices_exist,
            "no box prices exist": self._no_box_prices_exist,
            "a specific box price exists": self._specific_box_price_exists
        }
        
        # Verify the contract
        success, logs = self.verifier.verify_pacts(
            pact_files=[pact_file],
            provider_states_setup_url=f"{self.pact_uri}/pact-provider-state",
            provider_states=provider_states,
            verbose=True
        )
        
        # Log results
        for log in logs:
            logger.info(log)
        
        # Assert that verification was successful
        self.assertTrue(success)
    
    def _box_prices_exist(self, provider_state):
        """Set up state where box prices exist."""
        # Box prices are already created in setUp
        return True
    
    def _no_box_prices_exist(self, provider_state):
        """Set up state where no box prices exist."""
        BoxPrice.objects.all().delete()
        return True
    
    def _specific_box_price_exists(self, provider_state):
        """Set up state where a specific box price exists."""
        # Recreate box price with id=1 if it doesn't exist
        BoxPrice.objects.filter(id=1).delete()
        BoxPriceFactory(
            id=1,
            box_type='Specific Box',
            price=Decimal('7.99'),
            length=Decimal('7.50'),
            width=Decimal('6.25'),
            height=Decimal('4.75')
        )
        return True