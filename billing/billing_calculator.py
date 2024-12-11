# billing_calculator.py

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional, Union
import json
from django.core.exceptions import ValidationError
from django.db.models import Q
import logging

from orders.models import Order
from customers.models import Customer
from services.models import Service
from rules.models import Rule, RuleGroup
from customer_services.models import CustomerService

logger = logging.getLogger(__name__)

@dataclass
class ServiceCost:
    service_id: int
    service_name: str
    amount: Decimal

@dataclass
class OrderCost:
    order_id: int
    service_costs: List[ServiceCost] = field(default_factory=list)
    total_amount: Decimal = Decimal('0')

@dataclass
class BillingReport:
    customer_id: int
    start_date: datetime
    end_date: datetime
    order_costs: List[OrderCost] = field(default_factory=list)
    service_totals: Dict[int, Decimal] = field(default_factory=dict)
    total_amount: Decimal = Decimal('0')

class RuleEvaluator:
    @staticmethod
    def evaluate_rule(rule: Rule, order: Order) -> bool:
        try:
            field_value = getattr(order, rule.field, None)
            if field_value is None:
                logger.warning(f"Field {rule.field} not found in order {order.transaction_id}")
                return False

            values = rule.get_values_as_list()

            # Handle numeric fields
            numeric_fields = ['weight_lb', 'line_items', 'total_item_qty', 'volume_cuft', 'packages']
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
                             'carrier', 'notes']
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

            # Handle SKU quantity (JSON field)
            if rule.field == 'sku_quantity':
                if field_value is None:
                    return False

                try:
                    if isinstance(field_value, str):
                        field_value = json.loads(field_value)

                    if rule.operator == 'contains':
                        return any(v in field_value.keys() for v in values)
                    elif rule.operator == 'ncontains':
                        return not any(v in field_value.keys() for v in values)
                    elif rule.operator == 'in':
                        return any(v in str(field_value) for v in values)
                    elif rule.operator == 'ni':
                        return not any(v in str(field_value) for v in values)
                except (json.JSONDecodeError, AttributeError):
                    logger.error(f"Error processing SKU quantity: {field_value}")
                    return False

            logger.warning(f"Unhandled field {rule.field} or operator {rule.operator}")
            return False

        except Exception as e:
            logger.error(f"Error evaluating rule: {str(e)}")
            return False

    @staticmethod
    def evaluate_rule_group(rule_group: RuleGroup, order: Order) -> bool:
        try:
            rules = rule_group.rules.all()
            if not rules:
                logger.warning(f"No rules found in rule group {rule_group.id}")
                return False

            results = [RuleEvaluator.evaluate_rule(rule, order) for rule in rules]

            if rule_group.logic_operator == 'AND':
                return all(results)
            elif rule_group.logic_operator == 'OR':
                return any(results)
            elif rule_group.logic_operator == 'NOT':
                return not any(results)
            elif rule_group.logic_operator == 'XOR':
                return sum(results) == 1
            elif rule_group.logic_operator == 'NAND':
                return not all(results)
            elif rule_group.logic_operator == 'NOR':
                return not any(results)

            logger.warning(f"Unknown logic operator {rule_group.logic_operator}")
            return False

        except Exception as e:
            logger.error(f"Error evaluating rule group: {str(e)}")
            return False

class BillingCalculator:
    def __init__(self, customer_id: int, start_date: datetime, end_date: datetime):
        self.customer_id = customer_id
        self.start_date = start_date
        self.end_date = end_date
        self.report = BillingReport(customer_id, start_date, end_date)

    def validate_input(self) -> None:
        """Validate input parameters"""
        try:
            # Check customer exists
            try:
                customer = Customer.objects.get(id=self.customer_id)
            except Customer.DoesNotExist:
                raise ValidationError(f"Customer with ID {self.customer_id} not found")

            # Check date range
            if self.start_date > self.end_date:
                raise ValidationError("Start date must be before or equal to end date")

            # Check if customer has any services
            if not CustomerService.objects.filter(customer_id=self.customer_id).exists():
                raise ValidationError(f"No services found for customer {self.customer_id}")

        except Exception as e:
            logger.error(f"Validation error: {str(e)}")
            raise

    def calculate_service_cost(self, service: Service, order: Order, rule: Rule, customer_service: CustomerService) -> Decimal:
        """Calculate the cost for a service based on the rule, order, and customer service pricing"""
        try:
            if not customer_service.unit_price:
                logger.warning(f"No unit price set for customer service {customer_service}")
                return Decimal('0')

            # Get the base price from customer service
            base_price = customer_service.unit_price

            # Apply any rule adjustments if present
            adjustment = rule.adjustment_amount if rule.adjustment_amount else Decimal('0')

            # Calculate total cost based on service type
            if service.charge_type == 'single':
                return base_price + adjustment
            elif service.charge_type == 'quantity':
                quantity = getattr(order, 'total_item_qty', 1)
                if quantity is None:
                    quantity = 1
                quantity = Decimal(str(quantity))
                return (base_price + adjustment) * quantity

            logger.warning(f"Unknown charge type {service.charge_type} for service {service.id}")
            return Decimal('0')

        except Exception as e:
            logger.error(f"Error calculating service cost: {str(e)}")
            return Decimal('0')

    def generate_report(self) -> BillingReport:
        """Generate the billing report"""
        try:
            self.validate_input()

            # Fetch orders
            orders = Order.objects.filter(
                customer_id=self.customer_id,
                close_date__range=(self.start_date, self.end_date)
            ).select_related('customer')

            if not orders:
                logger.info(f"No orders found for customer {self.customer_id} in date range")
                return self.report

            # Fetch customer services and their rules
            customer_services = CustomerService.objects.filter(
                customer_id=self.customer_id
            ).select_related('service')

            # Process each order
            for order in orders:
                try:
                    order_cost = OrderCost(order_id=order.transaction_id)

                    for cs in customer_services:
                        rule_groups = RuleGroup.objects.filter(customer_service=cs)

                        # Check if any rule group applies
                        for rule_group in rule_groups:
                            if RuleEvaluator.evaluate_rule_group(rule_group, order):
                                # Calculate costs for applicable rules
                                for rule in rule_group.rules.all():
                                    cost = self.calculate_service_cost(
                                        service=cs.service,
                                        order=order,
                                        rule=rule,
                                        customer_service=cs
                                    )

                                    service_cost = ServiceCost(
                                        service_id=cs.service.id,
                                        service_name=cs.service.service_name,
                                        amount=cost
                                    )
                                    order_cost.service_costs.append(service_cost)
                                    order_cost.total_amount += cost

                                    # Update service totals
                                    self.report.service_totals[cs.service.id] = (
                                            self.report.service_totals.get(cs.service.id, Decimal('0')) + cost
                                    )

                    self.report.order_costs.append(order_cost)
                    self.report.total_amount += order_cost.total_amount

                except Exception as e:
                    logger.error(f"Error processing order {order.transaction_id}: {str(e)}")
                    continue

            return self.report

        except Exception as e:
            logger.error(f"Error generating report: {str(e)}")
            raise

    def to_dict(self) -> dict:
        """Convert the report to a dictionary format"""
        try:
            return {
                'customer_id': self.report.customer_id,
                'start_date': self.report.start_date.isoformat(),
                'end_date': self.report.end_date.isoformat(),
                'orders': [
                    {
                        'order_id': oc.order_id,
                        'services': [
                            {
                                'service_id': sc.service_id,
                                'service_name': sc.service_name,
                                'amount': str(sc.amount)
                            }
                            for sc in oc.service_costs
                        ],
                        'total_amount': str(oc.total_amount)
                    }
                    for oc in self.report.order_costs
                ],
                'service_totals': {
                    service_id: str(amount)
                    for service_id, amount in self.report.service_totals.items()
                },
                'total_amount': str(self.report.total_amount)
            }
        except Exception as e:
            logger.error(f"Error converting report to dict: {str(e)}")
            raise

    def to_json(self) -> str:
        """Convert the report to JSON format"""
        try:
            return json.dumps(self.to_dict(), indent=2)
        except Exception as e:
            logger.error(f"Error converting report to JSON: {str(e)}")
            raise

    def to_csv(self) -> str:
        """Convert the report to CSV format"""
        try:
            lines = [
                "Order ID,Service ID,Service Name,Amount",
            ]

            for order_cost in self.report.order_costs:
                for service_cost in order_cost.service_costs:
                    lines.append(
                        f"{order_cost.order_id},"
                        f"{service_cost.service_id},"
                        f"{service_cost.service_name},"
                        f"{service_cost.amount}"
                    )

            return "\n".join(lines)
        except Exception as e:
            logger.error(f"Error converting report to CSV: {str(e)}")
            raise

def generate_billing_report(
        customer_id: int,
        start_date: Union[datetime, str],
        end_date: Union[datetime, str],
        output_format: str = 'json'
) -> str:
    """
    Generate a billing report for the specified customer and date range.
    
    Args:
        customer_id: The ID of the customer
        start_date: Start date (datetime or ISO format string)
        end_date: End date (datetime or ISO format string)
        output_format: Output format ('json' or 'csv')
    
    Returns:
        str: The formatted report
    
    Raises:
        ValidationError: If input parameters are invalid
    """
    try:
        logger.info(f"Generating report for customer {customer_id} from {start_date} to {end_date}")

        # Convert string dates to datetime if necessary
        if isinstance(start_date, str):
            start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        if isinstance(end_date, str):
            end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))

        calculator = BillingCalculator(customer_id, start_date, end_date)
        calculator.generate_report()

        if output_format.lower() == 'csv':
            return calculator.to_csv()
        return calculator.to_json()

    except Exception as e:
        logger.error(f"Error in generate_billing_report: {str(e)}")
        raise