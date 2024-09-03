# billing/services/billing_calculator.py

from rules.models import RuleGroup
from orders.models import Order
from customer_services.models import CustomerService
from decimal import Decimal

class BillingCalculator:

    def __init__(self, customer, orders):
        self.customer = customer
        self.orders = orders
        self.total_cost = Decimal('0.00')
        self.order_details = []

    def apply_rules(self, service, order):
        """Apply rules to determine if a service should be charged for an order."""
        rule_groups = RuleGroup.objects.filter(customer_service__service=service, customer_service__customer=self.customer)
        for rule_group in rule_groups:
            rules = rule_group.rules.all()
            if rule_group.logic_operator == 'AND':
                if all(self.evaluate_rule(rule, order) for rule in rules):
                    return True
            elif rule_group.logic_operator == 'OR':
                if any(self.evaluate_rule(rule, order) for rule in rules):
                    return True
            elif rule_group.logic_operator == 'NOT':
                if not any(self.evaluate_rule(rule, order) for rule in rules):
                    return True
        return False

    def evaluate_rule(self, rule, order):
        """Evaluate a single rule against an order with context-specific validation."""
        order_value = getattr(order, rule.field, None)

        # Context-specific validation and interpretation
        if rule.field == 'sku_quantity' and isinstance(order_value, dict):
            if rule.operator == 'contains':
                return rule.value in order_value.keys()
            elif rule.operator == 'eq':
                try:
                    return order_value == eval(rule.value)
                except (SyntaxError, ValueError):
                    return False
            elif rule.operator == 'in':
                return any(item in order_value.keys() for item in rule.get_values_as_list())
            elif rule.operator == 'ni':
                return all(item not in order_value.keys() for item in rule.get_values_as_list())

        elif isinstance(order_value, str):
            # Handle string-based operators for string fields
            if rule.operator == 'contains' and rule.value in order_value:
                return True
            elif rule.operator == 'eq' and order_value == rule.value:
                return True
            elif rule.operator == 'startswith' and order_value.startswith(rule.value):
                return True
            elif rule.operator == 'endswith' and order_value.endswith(rule.value):
                return True
            elif rule.operator == 'in' and any(item in order_value for item in rule.get_values_as_list()):
                return True
            elif rule.operator == 'ni' and all(item not in order_value for item in rule.get_values_as_list()):
                return True

        elif isinstance(order_value, (int, float, Decimal)):
            # Handle numeric operators for numeric fields
            try:
                numeric_value = float(rule.value)
                if rule.operator == 'gt' and order_value > numeric_value:
                    return True
                elif rule.operator == 'lt' and order_value < numeric_value:
                    return True
                elif rule.operator == 'ge' and order_value >= numeric_value:
                    return True
                elif rule.operator == 'le' and order_value <= numeric_value:
                    return True
                elif rule.operator == 'eq' and order_value == numeric_value:
                    return True
                elif rule.operator == 'ne' and order_value != numeric_value:
                    return True
            except ValueError:
                return False

        # Default return False if no conditions are met
        return False

    def calculate_order_cost(self, order):
        # Calculate cost for a single order
        order_detail = {
            "transaction_id": order.transaction_id,
            "service": order.service_name,  # Replace with actual service attribute
            "cost": order.total_cost,  # Replace with actual cost attribute
            "close_date": order.close_date,
            "reference_number": order.reference_number,
            "ship_to_name": order.ship_to_name,
            "ship_to_company": order.ship_to_company,
            "ship_to_address": order.ship_to_address,
            "ship_to_address2": order.ship_to_address2,
            "ship_to_city": order.ship_to_city,
            "ship_to_state": order.ship_to_state,
            "ship_to_zip": order.ship_to_zip,
            "ship_to_country": order.ship_to_country,
            "weight_lb": order.weight_lb,
            "line_items": order.line_items,
            "sku_quantity": order.sku_quantity,
            "total_item_qty": order.total_item_qty,
            "volume_cuft": order.volume_cuft,
            "packages": order.packages,
            "notes": order.notes,
            "carrier": order.carrier,
        }
        self.order_details.append(order_detail)
        self.total_cost += order.total_cost

    def calculate_total_billing(self):
        for order in self.orders:
            self.calculate_order_cost(order)
        return self.total_cost, self.order_details
