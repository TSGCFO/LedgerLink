from django.test import TestCase
from django.db.utils import IntegrityError
from decimal import Decimal
from materials.models import Material, BoxPrice
from materials.tests.factories import MaterialFactory, BoxPriceFactory


class MaterialModelTest(TestCase):
    """Test suite for the Material model."""

    def setUp(self):
        """Set up test data."""
        self.material = MaterialFactory(
            name='Cardboard',
            description='Standard cardboard material for packaging',
            unit_price=Decimal('10.50')
        )

    def test_material_creation(self):
        """Test that a Material instance can be created."""
        self.assertIsInstance(self.material, Material)
        self.assertEqual(self.material.name, 'Cardboard')
        self.assertEqual(self.material.description, 'Standard cardboard material for packaging')
        self.assertEqual(self.material.unit_price, Decimal('10.50'))

    def test_string_representation(self):
        """Test the string representation of a Material."""
        self.assertEqual(str(self.material), 'Cardboard')

    def test_name_uniqueness(self):
        """Test that material names must be unique."""
        with self.assertRaises(IntegrityError):
            MaterialFactory(
                name='Cardboard',  # Same name as existing material
                description='Different description',
                unit_price=Decimal('12.75')
            )

    def test_unit_price_precision(self):
        """Test that unit_price handles decimal precision correctly."""
        material = MaterialFactory(
            name='Plastic',
            description='Plastic material',
            unit_price=Decimal('23.45')
        )
        
        # Check that the decimal is stored precisely
        self.assertEqual(material.unit_price, Decimal('23.45'))
        
        # Check that we can do calculations with the price
        tax_rate = Decimal('0.08')
        expected_tax = Decimal('1.88')  # 23.45 * 0.08 = 1.876, rounded to 1.88
        calculated_tax = round(material.unit_price * tax_rate, 2)
        self.assertEqual(calculated_tax, expected_tax)


class BoxPriceModelTest(TestCase):
    """Test suite for the BoxPrice model."""

    def setUp(self):
        """Set up test data."""
        self.box_price = BoxPriceFactory(
            box_type='Standard',
            price=Decimal('5.25'),
            length=Decimal('10.50'),
            width=Decimal('8.25'),
            height=Decimal('6.00')
        )

    def test_box_price_creation(self):
        """Test that a BoxPrice instance can be created."""
        self.assertIsInstance(self.box_price, BoxPrice)
        self.assertEqual(self.box_price.box_type, 'Standard')
        self.assertEqual(self.box_price.price, Decimal('5.25'))
        self.assertEqual(self.box_price.length, Decimal('10.50'))
        self.assertEqual(self.box_price.width, Decimal('8.25'))
        self.assertEqual(self.box_price.height, Decimal('6.00'))

    def test_string_representation(self):
        """Test the string representation of a BoxPrice."""
        self.assertEqual(str(self.box_price), 'Standard - 5.25')

    def test_multiple_box_types(self):
        """Test that multiple box types can be created."""
        small_box = BoxPriceFactory(
            box_type='Small',
            price=Decimal('3.50'),
            length=Decimal('5.00'),
            width=Decimal('4.00'),
            height=Decimal('3.00')
        )
        
        large_box = BoxPriceFactory(
            box_type='Large',
            price=Decimal('8.75'),
            length=Decimal('15.00'),
            width=Decimal('12.00'),
            height=Decimal('9.00')
        )
        
        # Check that all three box types exist
        self.assertEqual(BoxPrice.objects.count(), 3)
        
        # Verify the properties of the small box
        self.assertEqual(small_box.box_type, 'Small')
        self.assertEqual(small_box.price, Decimal('3.50'))
        
        # Verify the properties of the large box
        self.assertEqual(large_box.box_type, 'Large')
        self.assertEqual(large_box.price, Decimal('8.75'))

    def test_dimension_calculations(self):
        """Test calculations based on box dimensions."""
        # Calculate volume
        volume = self.box_price.length * self.box_price.width * self.box_price.height
        expected_volume = Decimal('10.50') * Decimal('8.25') * Decimal('6.00')
        self.assertEqual(volume, expected_volume)
        
        # Calculate surface area
        surface_area = 2 * (
            self.box_price.length * self.box_price.width +
            self.box_price.length * self.box_price.height +
            self.box_price.width * self.box_price.height
        )
        expected_surface_area = 2 * (
            Decimal('10.50') * Decimal('8.25') +
            Decimal('10.50') * Decimal('6.00') +
            Decimal('8.25') * Decimal('6.00')
        )
        self.assertEqual(surface_area, expected_surface_area)