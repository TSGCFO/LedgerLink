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

def convert_sku_format(sku_data) -> Dict:
    """
    Convert SKU data from JSON array format to dictionary format
    Input format: [{"sku": "ABO-022", "quantity": 720}]
    Output format: {'ABO-022': 720}
    """
    try:
        if isinstance(sku_data, str):
            sku_data = json.loads(sku_data)

        if not isinstance(sku_data, list):
            logger.error(f"SKU data must be a list, got {type(sku_data)}")
            return {}

        sku_dict = {}
        for item in sku_data:
            if not isinstance(item, dict):
                logger.error(f"Each SKU item must be a dictionary, got {type(item)}")
                continue

            if 'sku' not in item or 'quantity' not in item:
                logger.error("SKU item missing required fields 'sku' or 'quantity'")
                continue

            sku = str(item['sku']).strip().upper()  # Normalize SKU format
            try:
                quantity = float(item['quantity'])
            except (TypeError, ValueError):
                logger.error(f"Invalid quantity for SKU {sku}: {item['quantity']}")
                continue

            if not sku:
                logger.error("SKU cannot be empty")
                continue

            if quantity <= 0:
                logger.error(f"Invalid quantity {quantity} for SKU {sku}")
                continue

            sku_dict[sku] = quantity

        return sku_dict
    except (json.JSONDecodeError, TypeError, KeyError) as e:
        logger.error(f"Error converting SKU format: {str(e)}")
        return {}

def validate_sku_quantity(sku_data) -> bool:
    """Validate SKU quantity data format and content."""
    try:
        if isinstance(sku_data, str):
            sku_data = json.loads(sku_data)

        if not isinstance(sku_data, list):
            return False

        # Convert to dictionary
        sku_dict = convert_sku_format(sku_data)
        if not sku_dict:
            return False

        # Validate the converted dictionary
        for sku, quantity in sku_dict.items():
            if not isinstance(sku, str) or not sku.strip():
                return False

            try:
                qty = float(quantity)
                if qty <= 0:
                    return False
            except (TypeError, ValueError):
                return False

        return True
    except Exception as e:
        logger.error(f"Error validating SKU quantity: {str(e)}")
        return False

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

            # Handle SKU quantity
            if rule.field == 'sku_quantity':
                if field_value is None:
                    return False

                try:
                    if isinstance(field_value, str):
                        field_value = json.loads(field_value)

                    if not validate_sku_quantity(field_value):
                        return False

                    # Extract SKUs for comparison
                    sku_dict = convert_sku_format(field_value)
                    skus = list(sku_dict.keys())

                    if rule.operator == 'contains':
                        return any(v in skus for v in values)
                    elif rule.operator == 'ncontains':
                        return not any(v in skus for v in values)
                    elif rule.operator == 'in':
                        return any(v in str(sku_dict) for v in values)
                    elif rule.operator == 'ni':
                        return not any(v in str(sku_dict) for v in values)
                except (json.JSONDecodeError, AttributeError):
                    logger.error(f"Error processing SKU quantity")
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
            try:
                customer = Customer.objects.get(id=self.customer_id)
            except Customer.DoesNotExist:
                raise ValidationError(f"Customer with ID {self.customer_id} not found")

            if self.start_date > self.end_date:
                raise ValidationError("Start date must be before or equal to end date")

            if not CustomerService.objects.filter(customer_id=self.customer_id).exists():
                raise ValidationError(f"No services found for customer {self.customer_id}")

        except Exception as e:
            logger.error(f"Validation error: {str(e)}")
            raise

    def calculate_service_cost(self, customer_service: CustomerService, order: Order) -> Decimal:
        """Calculate the cost for a service"""
        try:
            if not customer_service.unit_price:
                logger.warning(f"No unit price set for customer service {customer_service}")
                return Decimal('0')

            base_price = customer_service.unit_price
            service_name = customer_service.service.service_name.lower()

            if customer_service.service.charge_type == 'single':
                return base_price
            elif customer_service.service.charge_type == 'quantity':
                # Special handling for SKU Cost service
                if service_name == 'sku cost':
                    try:
                        sku_quantity = getattr(order, 'sku_quantity', None)
                        if sku_quantity is None:
                            logger.warning(f"No sku_quantity found for order {order.transaction_id}")
                            return Decimal('0')

                        sku_dict = convert_sku_format(sku_quantity)
                        if not sku_dict:
                            logger.error(f"Invalid SKU quantity format for order {order.transaction_id}")
                            return Decimal('0')

                        unique_sku_count = len(sku_dict.keys())
                        total_cost = base_price * Decimal(str(unique_sku_count))

                        logger.info(
                            f"SKU Cost calculation details for order {order.transaction_id}:\n"
                            f"- Original SKU data: {sku_quantity}\n"
                            f"- Converted format: {sku_dict}\n"
                            f"- Unique SKUs: {list(sku_dict.keys())}\n"
                            f"- Number of unique SKUs: {unique_sku_count}\n"
                            f"- Base price per unique SKU: ${base_price}\n"
                            f"- Total cost ({unique_sku_count} SKUs × ${base_price}): ${total_cost}"
                        )
                        return total_cost

                    except Exception as e:
                        logger.error(f"Error processing SKU quantity for order {order.transaction_id}: {str(e)}")
                        return Decimal('0')

                # Special handling for Pick Cost and Case Pick services
                elif service_name in ['pick cost', 'case pick']:
                    try:
                        from products.models import Product

                        sku_quantity = getattr(order, 'sku_quantity', None)
                        if sku_quantity is None:
                            logger.warning(f"No sku_quantity found for order {order.transaction_id}")
                            return Decimal('0')

                        sku_dict = convert_sku_format(sku_quantity)
                        if not sku_dict:
                            logger.error(f"Invalid SKU quantity format for order {order.transaction_id}")
                            return Decimal('0')

                        total_cost = Decimal('0')
                        calculation_details = []
                        error_details = []

                        for sku, quantity in sku_dict.items():
                            try:
                                # Get product details from database
                                try:
                                    product = Product.objects.get(
                                        sku=sku,
                                        customer_id=order.customer_id
                                    )
                                except Product.DoesNotExist:
                                    error_msg = f"Product not found for SKU {sku} and customer {order.customer_id}"
                                    logger.error(error_msg)
                                    error_details.append(error_msg)
                                    continue

                                # Check if product has case quantity defined in labeling_unit_1
                                case_size = None
                                if (product.labeling_unit_1 and
                                        product.labeling_unit_1.lower() == 'case' and
                                        product.labeling_quantity_1):
                                    case_size = product.labeling_quantity_1
                                    logger.debug(
                                        f"Found case size for SKU {sku}: "
                                        f"{case_size} units per case"
                                    )

                                # Process based on service type
                                if service_name == 'case pick':
                                    if case_size:
                                        # Calculate number of full cases
                                        cases = quantity // case_size
                                        if cases > 0:
                                            case_cost = base_price * Decimal(str(cases))
                                            total_cost += case_cost
                                            calculation_details.append(
                                                f"SKU {sku}:\n"
                                                f"  - Total quantity: {quantity}\n"
                                                f"  - Case size: {case_size} units per case\n"
                                                f"  - Full cases: {cases}\n"
                                                f"  - Cost: {cases} cases × ${base_price} = ${case_cost}"
                                            )
                                        else:
                                            calculation_details.append(
                                                f"SKU {sku}: No full cases (quantity {quantity} < case size {case_size})"
                                            )
                                    else:
                                        calculation_details.append(
                                            f"SKU {sku}: No case size defined, skipping case pick calculation"
                                        )
                                else:  # pick cost
                                    if case_size:
                                        # Calculate remaining units that don't make a full case
                                        remaining_units = quantity % case_size
                                        if remaining_units > 0:
                                            unit_cost = base_price * Decimal(str(remaining_units))
                                            total_cost += unit_cost
                                            calculation_details.append(
                                                f"SKU {sku}:\n"
                                                f"  - Total quantity: {quantity}\n"
                                                f"  - Case size: {case_size} units per case\n"
                                                f"  - Remaining units: {remaining_units}\n"
                                                f"  - Cost: {remaining_units} units × ${base_price} = ${unit_cost}"
                                            )
                                    else:
                                        # If no case size defined or not a case unit, charge for all units
                                        unit_cost = base_price * Decimal(str(quantity))
                                        total_cost += unit_cost
                                        calculation_details.append(
                                            f"SKU {sku}:\n"
                                            f"  - Quantity: {quantity} units\n"
                                            f"  - Base unit: {product.labeling_unit_1}\n"
                                            f"  - Cost: {quantity} units × ${base_price} = ${unit_cost}"
                                        )

                            except Exception as e:
                                error_msg = f"Error processing SKU {sku}: {str(e)}"
                                logger.error(error_msg)
                                error_details.append(error_msg)
                                continue

                        # Log comprehensive calculation details
                        log_message = [
                            f"\n{service_name.upper()} calculation details for order {order.transaction_id}:",
                            f"Original SKU data: {sku_quantity}",
                            f"Converted format: {sku_dict}",
                            "\nCalculations:",
                            *calculation_details
                        ]

                        if error_details:
                            log_message.extend(["\nErrors encountered:", *error_details])

                        log_message.extend([
                            f"\nFinal Results:",
                            f"- Base price: ${base_price}",
                            f"- Total cost: ${total_cost}"
                        ])

                        logger.info("\n".join(log_message))
                        return total_cost

                    except Exception as e:
                        logger.error(
                            f"Error processing {service_name} for order {order.transaction_id}:\n"
                            f"Error: {str(e)}\n"
                            f"SKU data: {getattr(order, 'sku_quantity', 'N/A')}"
                        )
                        return Decimal('0')
                else:
                    # Regular quantity-based service
                    quantity = getattr(order, 'total_item_qty', 1)
                    if quantity is None:
                        quantity = 1
                    quantity = Decimal(str(quantity))
                    return base_price * quantity

            logger.warning(f"Unknown charge type {customer_service.service.charge_type} for service {customer_service.service.id}")
            return Decimal('0')

        except Exception as e:
            logger.error(f"Error calculating service cost for service {customer_service.service.service_name}: {str(e)}")
            return Decimal('0')

    def generate_report(self) -> BillingReport:
        """Generate the billing report"""
        try:
            self.validate_input()

            orders = Order.objects.filter(
                customer_id=self.customer_id,
                close_date__range=(self.start_date, self.end_date)
            ).select_related('customer')

            if not orders:
                logger.info(f"No orders found for customer {self.customer_id} in date range")
                return self.report

            customer_services = CustomerService.objects.filter(
                customer_id=self.customer_id
            ).select_related('service')

            for order in orders:
                try:
                    order_cost = OrderCost(order_id=order.transaction_id)
                    applied_single_services = set()

                    for cs in customer_services:
                        if cs.service.charge_type == 'single' and cs.service.id in applied_single_services:
                            continue

                        rule_groups = RuleGroup.objects.filter(customer_service=cs)
                        service_applies = False

                        if not rule_groups.exists():
                            service_applies = True  # If no rules, service always applies
                        else:
                            for rule_group in rule_groups:
                                if RuleEvaluator.evaluate_rule_group(rule_group, order):
                                    service_applies = True
                                    break

                        if service_applies:
                            cost = self.calculate_service_cost(cs, order)

                            service_cost = ServiceCost(
                                service_id=cs.service.id,
                                service_name=cs.service.service_name,
                                amount=cost
                            )
                            order_cost.service_costs.append(service_cost)
                            order_cost.total_amount += cost

                            self.report.service_totals[cs.service.id] = (
                                    self.report.service_totals.get(cs.service.id, Decimal('0')) + cost
                            )

                            if cs.service.charge_type == 'single':
                                applied_single_services.add(cs.service.id)

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
    """Generate a billing report for the specified customer and date range."""
    try:
        logger.info(f"Generating report for customer {customer_id} from {start_date} to {end_date}")

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

