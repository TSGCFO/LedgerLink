# bulk_operations/services/template_generator.py
from typing import Dict, List, Any


class CSVTemplateGenerator:
    """
    Service for generating CSV templates and managing template definitions.
    """

    @classmethod
    def get_available_templates(cls) -> List[Dict[str, Any]]:
        """
        Get list of available templates with their metadata.
        """
        return [
            {
                'type': 'customers',
                'name': 'Customers',
                'description': 'Import customer records',
                'fieldCount': len(cls._get_customer_fields()),
            },
            {
                'type': 'orders',
                'name': 'Orders',
                'description': 'Import order records',
                'fieldCount': len(cls._get_order_fields()),
            },
            {
                'type': 'products',
                'name': 'Products',
                'description': 'Import product records',
                'fieldCount': len(cls._get_product_fields()),
            },
            {
                'type': 'services',
                'name': 'Services',
                'description': 'Import service records',
                'fieldCount': len(cls._get_service_fields()),
            },
            {
                'type': 'materials',
                'name': 'Materials',
                'description': 'Import material records',
                'fieldCount': len(cls._get_material_fields()),
            },
            {
                'type': 'inserts',
                'name': 'Inserts',
                'description': 'Import insert records',
                'fieldCount': len(cls._get_insert_fields()),
            },
            {
                'type': 'cad_shipping',
                'name': 'CAD Shipping',
                'description': 'Import Canadian shipping records',
                'fieldCount': len(cls._get_cad_shipping_fields()),
            },
            {
                'type': 'us_shipping',
                'name': 'US Shipping',
                'description': 'Import US shipping records',
                'fieldCount': len(cls._get_us_shipping_fields()),
            },
        ]

    @classmethod
    def get_template_definition(cls, template_type: str) -> Dict[str, Any]:
        """
        Get template definition including fields and required fields.
        """
        template_map = {
            'customers': cls._get_customer_fields,
            'orders': cls._get_order_fields,
            'products': cls._get_product_fields,
            'services': cls._get_service_fields,
            'materials': cls._get_material_fields,
            'inserts': cls._get_insert_fields,
            'cad_shipping': cls._get_cad_shipping_fields,
            'us_shipping': cls._get_us_shipping_fields,
        }

        if template_type not in template_map:
            raise KeyError(f"Template type '{template_type}' not found")

        fields_method = template_map[template_type]
        fields = fields_method()
        return {
            'fields': list(fields.keys()),
            'required_fields': [f for f, v in fields.items() if v.get('required', False)],
        }

    @classmethod
    def get_field_types(cls, template_type: str) -> Dict[str, str]:
        """
        Get field types for a template.
        """
        template_map = {
            'customers': cls._get_customer_fields,
            'orders': cls._get_order_fields,
            'products': cls._get_product_fields,
            'services': cls._get_service_fields,
            'materials': cls._get_material_fields,
            'inserts': cls._get_insert_fields,
            'cad_shipping': cls._get_cad_shipping_fields,
            'us_shipping': cls._get_us_shipping_fields,
        }

        if template_type not in template_map:
            raise KeyError(f"Template type '{template_type}' not found")

        fields_method = template_map[template_type]
        fields = fields_method()
        return {name: field['type'] for name, field in fields.items()}

    @classmethod
    def generate_template_header(cls, template_type: str) -> List[str]:
        """
        Generate template header row.
        """
        definition = cls.get_template_definition(template_type)
        return definition['fields']

    @staticmethod
    def _get_customer_fields() -> Dict[str, Dict[str, Any]]:
        return {
            'company_name': {'type': 'string', 'required': True},
            'legal_business_name': {'type': 'string', 'required': True},
            'email': {'type': 'string', 'required': True},
            'phone': {'type': 'string', 'required': False},
            'address': {'type': 'string', 'required': False},
            'city': {'type': 'string', 'required': False},
            'state': {'type': 'string', 'required': False},
            'zip': {'type': 'string', 'required': False},
            'country': {'type': 'string', 'required': False},
            'business_type': {'type': 'string', 'required': False},
        }

    @staticmethod
    def _get_order_fields() -> Dict[str, Dict[str, Any]]:
        return {
            'transaction_id': {'type': 'integer', 'required': True, 'description': 'Primary key, externally assigned'},
            'customer': {'type': 'integer', 'required': True, 'description': 'Customer ID'},
            'close_date': {'type': 'datetime', 'required': False, 'description': 'Order close date (YYYY-MM-DD HH:MM:SS)'},
            'reference_number': {'type': 'string', 'required': True, 'description': 'External reference number'},
            'ship_to_name': {'type': 'string', 'required': True},
            'ship_to_company': {'type': 'string', 'required': False},
            'ship_to_address': {'type': 'string', 'required': True},
            'ship_to_address2': {'type': 'string', 'required': False},
            'ship_to_city': {'type': 'string', 'required': True},
            'ship_to_state': {'type': 'string', 'required': True},
            'ship_to_zip': {'type': 'string', 'required': True},
            'ship_to_country': {'type': 'string', 'required': False},
            'weight_lb': {'type': 'decimal', 'required': False, 'description': 'Weight in pounds'},
            'line_items': {'type': 'integer', 'required': False, 'description': 'Number of line items'},
            'sku_quantity': {
                'type': 'json',
                'required': False,
                'description': 'JSON object mapping SKUs to quantities, e.g., {"SKU1": 5, "SKU2": 3}. Leave empty if not applicable.'
            },
            'total_item_qty': {'type': 'integer', 'required': False, 'description': 'Total quantity of all items'},
            'volume_cuft': {'type': 'decimal', 'required': False, 'description': 'Volume in cubic feet'},
            'packages': {'type': 'integer', 'required': False, 'description': 'Number of packages'},
            'notes': {'type': 'string', 'required': False, 'description': 'Additional notes'},
            'carrier': {'type': 'string', 'required': False, 'description': 'Shipping carrier'},
            'status': {
                'type': 'choice',
                'required': False,
                'choices': [
                    ('draft', 'Draft'),
                    ('submitted', 'Submitted'),
                    ('shipped', 'Shipped'),
                    ('delivered', 'Delivered'),
                    ('cancelled', 'Cancelled')
                ],
                'default': 'draft',
                'description': 'Order status (draft, submitted, shipped, delivered, cancelled). Defaults to draft if empty.'
            },
            'priority': {
                'type': 'choice',
                'required': False,
                'choices': [
                    ('low', 'Low'),
                    ('medium', 'Medium'),
                    ('high', 'High')
                ],
                'default': 'medium',
                'description': 'Order priority (low, medium, high). Defaults to medium if empty.'
            },
        }

    @staticmethod
    def _get_product_fields() -> Dict[str, Dict[str, Any]]:
        return {
            'sku': {'type': 'string', 'required': True},
            'customer': {'type': 'integer', 'required': True},
            'labeling_unit_1': {'type': 'string', 'required': False},
            'labeling_quantity_1': {'type': 'integer', 'required': False},
            'labeling_unit_2': {'type': 'string', 'required': False},
            'labeling_quantity_2': {'type': 'integer', 'required': False},
            'labeling_unit_3': {'type': 'string', 'required': False},
            'labeling_quantity_3': {'type': 'integer', 'required': False},
            'labeling_unit_4': {'type': 'string', 'required': False},
            'labeling_quantity_4': {'type': 'integer', 'required': False},
            'labeling_unit_5': {'type': 'string', 'required': False},
            'labeling_quantity_5': {'type': 'integer', 'required': False},
        }

    @staticmethod
    def _get_service_fields() -> Dict[str, Dict[str, Any]]:
        return {
            'service_name': {'type': 'string', 'required': True},
            'description': {'type': 'string', 'required': False},
            'charge_type': {
                'type': 'choice',
                'required': True,
                'choices': [
                    ('single', 'Single Charge'),
                    ('quantity', 'Quantity Based')
                ],
                'description': 'How the service is charged (single: Single Charge, quantity: Quantity Based)'
            },
        }

    @staticmethod
    def _get_material_fields() -> Dict[str, Dict[str, Any]]:
        return {
            'name': {'type': 'string', 'required': True},
            'description': {'type': 'string', 'required': False},
            'unit_price': {'type': 'decimal', 'required': True},
        }

    @staticmethod
    def _get_insert_fields() -> Dict[str, Dict[str, Any]]:
        return {
            'sku': {'type': 'string', 'required': True},
            'insert_name': {'type': 'string', 'required': True},
            'insert_quantity': {'type': 'integer', 'required': True},
            'customer': {'type': 'integer', 'required': True},
        }

    @staticmethod
    def _get_cad_shipping_fields() -> Dict[str, Dict[str, Any]]:
        return {
            'transaction': {'type': 'integer', 'required': True},
            'customer': {'type': 'integer', 'required': True},
            'service_code_description': {'type': 'string', 'required': False},
            'ship_to_name': {'type': 'string', 'required': True},
            'ship_to_address_1': {'type': 'string', 'required': True},
            'ship_to_address_2': {'type': 'string', 'required': False},
            'shiptoaddress3': {'type': 'string', 'required': False},
            'ship_to_city': {'type': 'string', 'required': True},
            'ship_to_state': {'type': 'string', 'required': True},
            'ship_to_country': {'type': 'string', 'required': False},
            'ship_to_postal_code': {'type': 'string', 'required': True},
            'tracking_number': {'type': 'string', 'required': False},
            'pre_tax_shipping_charge': {'type': 'decimal', 'required': False},
            'tax1type': {'type': 'string', 'required': False},
            'tax1amount': {'type': 'decimal', 'required': False},
            'tax2type': {'type': 'string', 'required': False},
            'tax2amount': {'type': 'decimal', 'required': False},
            'tax3type': {'type': 'string', 'required': False},
            'tax3amount': {'type': 'decimal', 'required': False},
            'fuel_surcharge': {'type': 'decimal', 'required': False},
            'reference': {'type': 'string', 'required': False},
            'weight': {'type': 'decimal', 'required': False},
            'gross_weight': {'type': 'decimal', 'required': False},
            'box_length': {'type': 'decimal', 'required': False},
            'box_width': {'type': 'decimal', 'required': False},
            'box_height': {'type': 'decimal', 'required': False},
            'box_name': {'type': 'string', 'required': False},
            'carrier': {'type': 'string', 'required': False},
        }

    @staticmethod
    def _get_us_shipping_fields() -> Dict[str, Dict[str, Any]]:
        return {
            'transaction': {'type': 'integer', 'required': True},
            'customer': {'type': 'integer', 'required': True},
            'ship_date': {'type': 'date', 'required': False},
            'ship_to_name': {'type': 'string', 'required': True},
            'ship_to_address_1': {'type': 'string', 'required': True},
            'ship_to_address_2': {'type': 'string', 'required': False},
            'ship_to_city': {'type': 'string', 'required': True},
            'ship_to_state': {'type': 'string', 'required': True},
            'ship_to_zip': {'type': 'string', 'required': True},
            'ship_to_country_code': {'type': 'string', 'required': False},
            'tracking_number': {'type': 'string', 'required': False},
            'service_name': {'type': 'string', 'required': False},
            'weight_lbs': {'type': 'decimal', 'required': False},
            'length_in': {'type': 'decimal', 'required': False},
            'width_in': {'type': 'decimal', 'required': False},
            'height_in': {'type': 'decimal', 'required': False},
            'base_chg': {'type': 'decimal', 'required': False},
            'carrier_peak_charge': {'type': 'decimal', 'required': False},
            'wizmo_peak_charge': {'type': 'decimal', 'required': False},
            'accessorial_charges': {'type': 'decimal', 'required': False},
            'rate': {'type': 'decimal', 'required': False},
            'hst': {'type': 'decimal', 'required': False},
            'gst': {'type': 'decimal', 'required': False},
            'current_status': {'type': 'string', 'required': False},
            'delivery_status': {'type': 'string', 'required': False},
        }