# rules/models.py

from django.core.exceptions import ValidationError
from django.db import models
from customer_services.models import CustomerService
import json
import logging
import re

logger = logging.getLogger(__name__)


def validate_sku_quantity(value):
    """Validate the SKU quantity format"""
    if not isinstance(value, (list, dict)):
        return False

    # If it's a list, each item should be a dict with 'sku' and 'quantity'
    if isinstance(value, list):
        return all(
            isinstance(item, dict) and
            'sku' in item and
            'quantity' in item and
            isinstance(item['quantity'], (int, float))
            for item in value
        )

    # If it's a dict, each value should be a quantity
    return all(isinstance(v, (int, float)) for v in value.values())


def convert_sku_format(value):
    """Convert SKU quantity to standard format"""
    if isinstance(value, list):
        return {item['sku']: item['quantity'] for item in value}
    return value


def normalize_sku(sku):
    """Normalize SKU for comparison"""
    return str(sku).strip().upper()


class RuleGroup(models.Model):
    """
    A group of rules with a logical operator that determines how the rules are combined.
    
    Rules within a group are combined using the logic_operator, which can be one of:
    AND: All rules must evaluate to True
    OR: At least one rule must evaluate to True
    NOT: No rules should evaluate to True
    XOR: Exactly one rule must evaluate to True
    NAND: At least one rule must evaluate to False
    NOR: All rules must evaluate to False
    """
    LOGIC_CHOICES = [
        ('AND', 'All conditions must be true (AND)'),
        ('OR', 'Any condition can be true (OR)'),
        ('NOT', 'Condition must not be true (NOT)'),
        ('XOR', 'Only one condition must be true (XOR)'),
        ('NAND', 'At least one condition must be false (NAND)'),
        ('NOR', 'None of the conditions must be true (NOR)'),
    ]

    customer_service = models.ForeignKey(
        CustomerService, 
        on_delete=models.CASCADE,
        db_index=True,  # Add index for improved query performance
        help_text="The customer service this rule group applies to"
    )
    logic_operator = models.CharField(
        max_length=5, 
        choices=LOGIC_CHOICES, 
        default='AND',
        help_text="Logic operator to apply when evaluating rules in this group"
    )

    def __str__(self):
        return f"Rule Group for {self.customer_service} ({self.get_logic_operator_display()})"

    def evaluate(self, order):
        """Evaluate all rules in the group according to the logic operator"""
        rules = list(self.rules.all())
        if not rules:
            return True

        evaluator = RuleEvaluator()
        results = [evaluator.evaluate_rule(rule, order) for rule in rules]

        if self.logic_operator == 'AND':
            return all(results)
        elif self.logic_operator == 'OR':
            return any(results)
        elif self.logic_operator == 'NOT':
            return not any(results)
        elif self.logic_operator == 'XOR':
            return sum(results) == 1
        elif self.logic_operator == 'NAND':
            return not all(results)
        elif self.logic_operator == 'NOR':
            return not any(results)
        return False


class Rule(models.Model):
    """
    Basic rule that evaluates a condition on an order field and applies a price adjustment.
    
    A rule consists of a field, operator, and value that are evaluated against
    an order to determine if the rule applies. If the rule applies, the adjustment_amount
    can be applied to modify pricing.
    """
    FIELD_CHOICES = [
        ('reference_number', 'Reference Number'),
        ('ship_to_name', 'Ship To Name'),
        ('ship_to_company', 'Ship To Company'),
        ('ship_to_city', 'Ship To City'),
        ('ship_to_state', 'Ship To State'),
        ('ship_to_country', 'Ship To Country'),
        ('sku_count', 'SKU Count'),
        ('sku_name', 'SKU Name'),
        ('sku_quantity', 'SKU Quantity'),
        ('total_item_qty', 'Total Item Quantity'),
        ('packages', 'Packages'),
        ('notes', 'Notes'),
        ('carrier', 'Carrier'),
        ('volume_cuft', 'Volume (cuft)'),
        ('weight_lb', 'Weight (lb)'),
        ('line_items', 'Line Items'),
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
        ('only_contains', 'Only Contains'),
        ('startswith', 'Starts with'),
        ('endswith', 'Ends with'),
    ]

    rule_group = models.ForeignKey(
        RuleGroup, 
        on_delete=models.CASCADE, 
        related_name='rules',
        db_index=True,  # Add index for improved query performance
        help_text="The rule group this rule belongs to"
    )
    field = models.CharField(
        max_length=50, 
        choices=FIELD_CHOICES,
        db_index=True,  # Add index for improved filtering
        help_text="Order field to evaluate"
    )
    operator = models.CharField(
        max_length=15, 
        choices=OPERATOR_CHOICES,
        help_text="Comparison operator"
    )
    value = models.CharField(
        max_length=255, 
        help_text="For multiple values, separate them with a semicolon (;)"
    )
    adjustment_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Amount to adjust the price when this rule applies"
    )

    def __str__(self):
        return f"{self.get_field_display()} {self.get_operator_display()} {self.value} -> {self.adjustment_amount}"

    def clean(self):
        """Validate field and operator combinations"""
        values = self.get_values_as_list()

        # String field validation
        if self.field in ['reference_number', 'ship_to_name', 'ship_to_company', 'ship_to_city',
                          'ship_to_state', 'ship_to_country', 'carrier', 'sku_name', 'notes']:
            if self.operator in ['gt', 'lt', 'ge', 'le']:
                raise ValidationError(f"Operator '{self.get_operator_display()}' is not valid for string fields.")

        # Numeric field validation
        elif self.field in ['weight_lb', 'line_items', 'total_item_qty', 'volume_cuft', 'sku_count', 'packages']:
            if self.operator in ['contains', 'ncontains', 'startswith', 'endswith', 'only_contains']:
                raise ValidationError(f"Operator '{self.get_operator_display()}' is not valid for numeric fields.")
            if self.operator in ['gt', 'lt', 'ge', 'le', 'eq', 'ne']:
                try:
                    [float(v) for v in values]
                except ValueError:
                    raise ValidationError(f"Operator '{self.get_operator_display()}' requires numeric values.")

        # SKU quantity validation
        elif self.field == 'sku_quantity':
            if self.operator in ['gt', 'lt', 'ge', 'le', 'startswith', 'endswith']:
                raise ValidationError(f"Operator '{self.get_operator_display()}' is not valid for SKU quantity.")
            # Validate SKU format for relevant operators
            if self.operator in ['contains', 'ncontains', 'only_contains']:
                if not values:
                    raise ValidationError("At least one SKU must be specified")

        super().clean()

    def get_values_as_list(self):
        """Convert semicolon-separated values to list"""
        if not self.value:
            return []
        return [v.strip() for v in self.value.split(';') if v.strip()]

    def apply_adjustment(self, base_amount):
        """Apply rule adjustment to base amount"""
        if self.adjustment_amount is None:
            return base_amount
        return base_amount + self.adjustment_amount


class AdvancedRule(Rule):
    """
    Extended Rule model with complex conditions and calculations.
    
    AdvancedRule extends the basic Rule model with:
    1. Additional conditions as a JSON structure
    2. Complex calculation methods that go beyond simple adjustment amounts
    3. Tiered pricing configurations for case-based pricing
    
    This model supports various pricing strategies including flat fees, percentages,
    per-unit pricing, weight/volume-based pricing, tiered pricing, and product-specific rates.
    """

    CALCULATION_TYPES = [
        'flat_fee',        # Add fixed amount
        'percentage',      # Add percentage of base price
        'per_unit',        # Multiply by quantity
        'weight_based',    # Multiply by weight
        'volume_based',    # Multiply by volume
        'tiered_percentage', # Apply percentage based on value tiers
        'product_specific', # Apply specific rates per product
        'case_based_tier'  # New type for case-based calculations
    ]

    conditions = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional conditions as JSON: {'field': {'operator': 'value'}}"
    )

    calculations = models.JSONField(
        default=list,
        blank=True,
        help_text="Calculation steps as JSON: [{'type': 'calculation_type', 'value': number}]"
    )

    tier_config = models.JSONField(
        default=dict,
        blank=True,
        help_text="Configuration for tiered calculations: {'ranges': [{'min': x, 'max': y, 'multiplier': z}], 'excluded_skus': []}"
    )

    class Meta:
        verbose_name = "Advanced Rule"
        verbose_name_plural = "Advanced Rules"

    def clean(self):
        """Validate advanced rule structure"""
        super().clean()

        # Validate tier configuration for case_based_tier
        if any(calc.get('type') == 'case_based_tier' for calc in self.calculations):
            if not self.tier_config:
                raise ValidationError({
                    'tier_config': 'Tier configuration is required for case-based tier calculations'
                })

            if 'ranges' not in self.tier_config:
                raise ValidationError({
                    'tier_config': 'Ranges must be specified in tier configuration'
                })

            ranges = self.tier_config.get('ranges', [])
            if not isinstance(ranges, list):
                raise ValidationError({
                    'tier_config': 'Ranges must be a list of tier configurations'
                })

            for tier in ranges:
                if not all(k in tier for k in ('min', 'max', 'multiplier')):
                    raise ValidationError({
                        'tier_config': 'Each tier must specify min, max, and multiplier values'
                    })

                try:
                    min_val = float(tier['min'])
                    max_val = float(tier['max'])
                    multiplier = float(tier['multiplier'])

                    if min_val < 0 or max_val < 0 or multiplier < 0:
                        raise ValidationError({
                            'tier_config': 'Min, max, and multiplier values must be non-negative'
                        })

                    if min_val > max_val:
                        raise ValidationError({
                            'tier_config': f'Min value ({min_val}) cannot be greater than max value ({max_val})'
                        })

                except (TypeError, ValueError):
                    raise ValidationError({
                        'tier_config': 'Min, max, and multiplier values must be valid numbers'
                    })

            # Validate excluded_skus if present
            excluded_skus = self.tier_config.get('excluded_skus', [])
            if excluded_skus and not isinstance(excluded_skus, list):
                raise ValidationError({
                    'tier_config': 'excluded_skus must be a list of SKU strings'
                })

        # Validate conditions
        if self.conditions:
            if not isinstance(self.conditions, dict):
                raise ValidationError({'conditions': 'Conditions must be a JSON object'})

            for field, criteria in self.conditions.items():
                if not isinstance(criteria, dict):
                    raise ValidationError({'conditions': f'Criteria for field {field} must be a JSON object'})

                if not all(isinstance(k, str) and isinstance(v, (str, int, float))
                           for k, v in criteria.items()):
                    raise ValidationError(
                        {'conditions': f'Invalid criteria format for field {field}'}
                    )

        # Validate calculations
        if self.calculations:
            if not isinstance(self.calculations, list):
                raise ValidationError({'calculations': 'Calculations must be a JSON array'})

            for calc in self.calculations:
                if not isinstance(calc, dict):
                    raise ValidationError({'calculations': 'Each calculation must be a JSON object'})

                if 'type' not in calc or 'value' not in calc:
                    raise ValidationError(
                        {'calculations': 'Each calculation must have "type" and "value" fields'}
                    )

                if calc['type'] not in self.CALCULATION_TYPES:
                    raise ValidationError(
                        {'calculations': f'Invalid calculation type: {calc["type"]}'}
                    )

                try:
                    float(calc['value'])
                except (TypeError, ValueError):
                    raise ValidationError(
                        {'calculations': f'Invalid numeric value in calculation: {calc["value"]}'}
                    )

    def apply_adjustment(self, order, base_amount):
        """Apply advanced calculations to base amount"""
        try:
            amount = super().apply_adjustment(base_amount)

            if not self.calculations:
                return amount

            for calc in self.calculations:
                calc_type = calc['type']
                value = float(calc['value'])

                if calc_type == 'flat_fee':
                    amount += value
                elif calc_type == 'percentage':
                    amount += amount * (value / 100)
                elif calc_type == 'per_unit':
                    amount += order.total_item_qty * value
                elif calc_type == 'weight_based':
                    if order.weight_lb:
                        amount += float(order.weight_lb) * value
                elif calc_type == 'volume_based':
                    if order.volume_cuft:
                        amount += float(order.volume_cuft) * value
                elif calc_type == 'tiered_percentage':
                    if 'tiers' in calc:
                        for tier in calc['tiers']:
                            if amount >= tier['min'] and amount <= tier['max']:
                                amount += amount * (tier['percentage'] / 100)
                                break
                elif calc_type == 'product_specific':
                    if order.sku_quantity:
                        sku_data = json.loads(order.sku_quantity) if isinstance(order.sku_quantity,
                                                                                str) else order.sku_quantity
                        sku_dict = convert_sku_format(sku_data)
                        for sku, qty in sku_dict.items():
                            if sku in calc.get('rates', {}):
                                amount += qty * calc['rates'][sku]

            return amount

        except Exception as e:
            logger.error(f"Error applying calculations: {str(e)}")
            return base_amount


class RuleEvaluator:
    @staticmethod
    def evaluate_rule(rule: Rule, order) -> bool:
        try:
            field_value = getattr(order, rule.field, None)
            if field_value is None:
                logger.warning(f"Field {rule.field} not found in order {order.transaction_id}")
                return False

            values = rule.get_values_as_list()

            # Handle numeric fields
            numeric_fields = ['weight_lb', 'line_items', 'total_item_qty', 'volume_cuft', 'packages', 'sku_count']
            if rule.field in numeric_fields:
                try:
                    field_value = float(field_value) if field_value is not None else 0
                    value = float(values[0]) if values else 0

                    if rule.operator == 'gt':
                        return field_value > value
                    elif rule.operator == 'lt':
                        return field_value < value
                    elif rule.operator == 'eq':
                        return field_value == value
                    elif rule.operator == 'ne':
                        return field_value != value
                    elif rule.operator == 'ge':
                        return field_value >= value
                    elif rule.operator == 'le':
                        return field_value <= value
                except (ValueError, TypeError):
                    logger.error(f"Error converting numeric values for field {rule.field}")
                    return False

            # Handle string fields
            string_fields = ['reference_number', 'ship_to_name', 'ship_to_company',
                              'ship_to_city', 'ship_to_state', 'ship_to_country',
                              'carrier', 'notes', 'sku_name']
            if rule.field in string_fields:
                field_value = str(field_value) if field_value is not None else ''

                if rule.operator == 'eq':
                    return field_value == values[0]
                elif rule.operator == 'ne':
                    return field_value != values[0]
                elif rule.operator == 'in':
                    return field_value in values
                elif rule.operator == 'ni':
                    return field_value not in values
                elif rule.operator == 'contains':
                    return any(v in field_value for v in values)
                elif rule.operator == 'ncontains':
                    return not any(v in field_value for v in values)
                elif rule.operator == 'startswith':
                    return any(field_value.startswith(v) for v in values)
                elif rule.operator == 'endswith':
                    return any(field_value.endswith(v) for v in values)

            # Handle SKU quantity
            if rule.field == 'sku_quantity':
                if field_value is None:
                    return False

                try:
                    # Parse JSON if field_value is a string
                    if isinstance(field_value, str):
                        field_value = json.loads(field_value)

                    if not validate_sku_quantity(field_value):
                        logger.error(f"Invalid SKU quantity format in order {order.transaction_id}")
                        return False

                    # Convert to standard format and normalize SKUs
                    order_skus = convert_sku_format(field_value)
                    order_sku_set = {normalize_sku(sku) for sku in order_skus.keys()}
                    rule_sku_set = {normalize_sku(v) for v in values}

                    if rule.operator == 'only_contains':
                        # Check if all SKUs in the order are in the rule's SKU list
                        if not order_sku_set:  # Handle empty order SKUs
                            return False
                        return order_sku_set.issubset(rule_sku_set)

                    elif rule.operator == 'contains':
                        # Check if any rule SKU exists in order SKUs
                        return any(sku in order_sku_set for sku in rule_sku_set)

                    elif rule.operator == 'ncontains':
                        # Check if none of the rule SKUs exist in order SKUs
                        return not any(sku in order_sku_set for sku in rule_sku_set)

                    elif rule.operator == 'in':
                        # Check if all order SKUs exist in rule SKUs
                        return all(sku in rule_sku_set for sku in order_sku_set)

                    elif rule.operator == 'ni':
                        # Check if none of the order SKUs exist in rule SKUs
                        return not any(sku in rule_sku_set for sku in order_sku_set)

                except (json.JSONDecodeError, AttributeError) as e:
                    logger.error(f"Error processing SKU quantity for order {order.transaction_id}: {str(e)}")
                    return False

            logger.warning(f"Unhandled field {rule.field} or operator {rule.operator}")
            return False

        except Exception as e:
            logger.error(f"Error evaluating rule: {str(e)}")
            return False