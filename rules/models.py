# rules/models.py

from django.core.exceptions import ValidationError
from django.db import models
from customer_services.models import CustomerService

class RuleGroup(models.Model):
    LOGIC_CHOICES = [
        ('AND', 'All conditions must be true (AND)'),
        ('OR', 'Any condition can be true (OR)'),
        ('NOT', 'Condition must not be true (NOT)'),
        ('XOR', 'Only one condition must be true (XOR)'),
        ('NAND', 'At least one condition must be false (NAND)'),
        ('NOR', 'None of the conditions must be true (NOR)'),
    ]

    customer_service = models.ForeignKey(CustomerService, on_delete=models.CASCADE)
    logic_operator = models.CharField(max_length=5, choices=LOGIC_CHOICES, default='AND')

    def __str__(self):
        return f"Rule Group for {self.customer_service} ({self.get_logic_operator_display()})"


class Rule(models.Model):
    FIELD_CHOICES = [
        ('reference_number', 'Reference Number'),
        ('ship_to_name', 'Ship To Name'),
        ('ship_to_company', 'Ship To Company'),
        ('ship_to_city', 'Ship To City'),
        ('ship_to_state', 'Ship To State'),
        ('ship_to_country', 'Ship To Country'),
        ('weight_lb', 'Weight (lb)'),
        ('line_items', 'Line Items'),
        ('sku_quantity', 'SKU Quantity'),
        ('total_item_qty', 'Total Item Quantity'),
        ('packages', 'Packages'),
        ('notes', 'Notes'),
        ('carrier', 'Carrier'),
        ('volume_cuft', 'Volume (cuft)'),
    ]

    OPERATOR_CHOICES = [
        ('gt', 'Greater than'),
        ('lt', 'Less than'),
        ('eq', 'Equals'),
        ('ne', 'Not equals'),
        ('ge', 'Greater than or equals'),
        ('le', 'Less than or equals'),
        ('in', 'In'),
        ('ni', 'Not in'),
        ('contains', 'Contains'),
        ('ncontains', 'Not contains'),
        ('startswith', 'Starts with'),
        ('endswith', 'Ends with'),
    ]

    rule_group = models.ForeignKey(RuleGroup, on_delete=models.CASCADE, related_name='rules')
    field = models.CharField(max_length=50, choices=FIELD_CHOICES)
    operator = models.CharField(max_length=10, choices=OPERATOR_CHOICES)
    value = models.CharField(max_length=255, help_text="For multiple values, separate them with a semicolon (;)")

    adjustment_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True,
                                            help_text="Amount to adjust the price")

    def __str__(self):
        return f"{self.get_field_display()} {self.get_operator_display()} {self.value} -> {self.adjustment_amount}"

    def clean(self):
        """Basic validation to ensure field and operator combination makes sense."""
        values = self.get_values_as_list()

        # String field validation
        if self.field in ['reference_number', 'ship_to_name', 'ship_to_company', 'ship_to_city',
                          'ship_to_state', 'ship_to_zip', 'ship_to_country', 'carrier', 'notes']:
            if self.operator in ['gt', 'lt', 'ge', 'le']:
                raise ValidationError(f"Operator '{self.get_operator_display()}' is not valid for string fields.")

        # Numeric field validation
        elif self.field in ['weight_lb', 'line_items', 'total_item_qty', 'volume_cuft', 'packages']:
            if self.operator in ['contains', 'ncontains', 'startswith', 'endswith']:
                raise ValidationError(f"Operator '{self.get_operator_display()}' is not valid for numeric fields.")
            if self.operator in ['gt', 'lt', 'ge', 'le', 'eq', 'ne']:
                try:
                    [float(v) for v in values]
                except ValueError:
                    raise ValidationError(f"Operator '{self.get_operator_display()}' requires numeric values.")

        # JSON field validation (basic)
        elif self.field == 'sku_quantity':
            if self.operator in ['contains', 'ncontains', 'in', 'ni']:
                # Allow basic list of keys or values
                pass
            elif self.operator in ['gt', 'lt', 'ge', 'le']:
                raise ValidationError(f"Operator '{self.get_operator_display()}' is not valid for JSON fields.")

        super().clean()

    def get_values_as_list(self):
        """Utility method to return the value field as a list of individual items."""
        return [v.strip() for v in self.value.split(';') if v.strip()]
