from django.test import TestCase
from decimal import Decimal
from materials.serializers import MaterialSerializer, BoxPriceSerializer
from materials.tests.factories import MaterialFactory, BoxPriceFactory


class MaterialSerializerTest(TestCase):
    """Test suite for the MaterialSerializer."""

    def setUp(self):
        """Set up test data."""
        self.material = MaterialFactory(
            name='Cardboard',
            description='Standard cardboard material for packaging',
            unit_price=Decimal('10.50')
        )
        self.serializer = MaterialSerializer(instance=self.material)

    def test_contains_expected_fields(self):
        """Test that the serializer contains the expected fields."""
        data = self.serializer.data
        expected_fields = ['id', 'name', 'description', 'unit_price']
        self.assertEqual(set(data.keys()), set(expected_fields))

    def test_unit_price_field_content(self):
        """Test that the unit_price field contains the correct value."""
        data = self.serializer.data
        self.assertEqual(Decimal(data['unit_price']), Decimal('10.50'))

    def test_validity_with_valid_data(self):
        """Test that the serializer is valid with valid data."""
        data = {
            'name': 'Plastic',
            'description': 'Plastic material for packaging',
            'unit_price': '15.75'
        }
        serializer = MaterialSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_invalidity_with_negative_price(self):
        """Test that the serializer is invalid with a negative price."""
        data = {
            'name': 'Plastic',
            'description': 'Plastic material for packaging',
            'unit_price': '-5.00'  # Negative price
        }
        serializer = MaterialSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('unit_price', serializer.errors)

    def test_create_material(self):
        """Test creating a new material using the serializer."""
        data = {
            'name': 'Foam',
            'description': 'Protective foam padding',
            'unit_price': '8.25'
        }
        serializer = MaterialSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        material = serializer.save()
        
        self.assertEqual(material.name, 'Foam')
        self.assertEqual(material.description, 'Protective foam padding')
        self.assertEqual(material.unit_price, Decimal('8.25'))


class BoxPriceSerializerTest(TestCase):
    """Test suite for the BoxPriceSerializer."""

    def setUp(self):
        """Set up test data."""
        self.box_price = BoxPriceFactory(
            box_type='Standard',
            price=Decimal('5.25'),
            length=Decimal('10.50'),
            width=Decimal('8.25'),
            height=Decimal('6.00')
        )
        self.serializer = BoxPriceSerializer(instance=self.box_price)

    def test_contains_expected_fields(self):
        """Test that the serializer contains the expected fields."""
        data = self.serializer.data
        expected_fields = ['id', 'box_type', 'price', 'length', 'width', 'height']
        self.assertEqual(set(data.keys()), set(expected_fields))

    def test_price_field_content(self):
        """Test that the price field contains the correct value."""
        data = self.serializer.data
        self.assertEqual(Decimal(data['price']), Decimal('5.25'))

    def test_dimension_fields_content(self):
        """Test that the dimension fields contain the correct values."""
        data = self.serializer.data
        self.assertEqual(Decimal(data['length']), Decimal('10.50'))
        self.assertEqual(Decimal(data['width']), Decimal('8.25'))
        self.assertEqual(Decimal(data['height']), Decimal('6.00'))

    def test_validity_with_valid_data(self):
        """Test that the serializer is valid with valid data."""
        data = {
            'box_type': 'Small',
            'price': '3.50',
            'length': '5.00',
            'width': '4.00',
            'height': '3.00'
        }
        serializer = BoxPriceSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_invalidity_with_negative_dimensions(self):
        """Test that the serializer is invalid with negative dimensions."""
        data = {
            'box_type': 'Small',
            'price': '3.50',
            'length': '-5.00',  # Negative length
            'width': '4.00',
            'height': '3.00'
        }
        serializer = BoxPriceSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('length', serializer.errors)

    def test_create_box_price(self):
        """Test creating a new box price using the serializer."""
        data = {
            'box_type': 'Large',
            'price': '8.75',
            'length': '15.00',
            'width': '12.00',
            'height': '9.00'
        }
        serializer = BoxPriceSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        box_price = serializer.save()
        
        self.assertEqual(box_price.box_type, 'Large')
        self.assertEqual(box_price.price, Decimal('8.75'))
        self.assertEqual(box_price.length, Decimal('15.00'))
        self.assertEqual(box_price.width, Decimal('12.00'))
        self.assertEqual(box_price.height, Decimal('9.00'))