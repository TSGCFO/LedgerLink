from rules.models import RuleGroup, Rule
from customer_services.models import CustomerService
import json
from decimal import Decimal

def is_single_charge_service(service_name):
    """
    Determine if a service should be charged only once per order.
    """
    single_charge_keywords = ['Base', 'RUSH ORDER', 'R-rush receiving', 'CROSS DOCK', 'RUSH']
    return any(keyword in service_name for keyword in single_charge_keywords)

def is_multi_charge_service(service_name):
    """
    Determine if a service can be charged multiple times per order.
    """
    multi_charge_keywords = ['Pick', 'SKU', 'RE LABELLING', 'R-BOX', 'R-PALLET', 'R-SKU', 'inserts', 'MATCHA TEA', 'FLATBOX']
    return any(keyword in service_name for keyword in multi_charge_keywords)

def apply_rules(order, customer):
    """
    Apply billing rules to determine which services should be charged for an order.
    """
    applicable_services = []
    customer_services = CustomerService.objects.filter(customer=customer)
    charged_services = set()  # Keep track of services already charged

    for customer_service in customer_services:
        rule_groups = RuleGroup.objects.filter(customer_service=customer_service)
        service_name = customer_service.service.service_name

        for rule_group in rule_groups:
            if evaluate_rule_group(rule_group, order):
                if is_single_charge_service(service_name):
                    if service_name in charged_services:
                        continue  # Skip if already charged
                    charged_services.add(service_name)
                    adjustment_amount = Decimal(rule_group.rules.first().adjustment_amount or 0)
                elif is_multi_charge_service(service_name):
                    adjustment_amount = sum(Decimal(rule.adjustment_amount or 0) for rule in rule_group.rules.all())
                else:
                    # For services not fitting either category, charge once by default
                    if service_name in charged_services:
                        continue
                    charged_services.add(service_name)
                    adjustment_amount = Decimal(rule_group.rules.first().adjustment_amount or 0)

                applicable_services.append((customer_service, adjustment_amount))
                break  # Stop checking rule groups for this service once one is satisfied

    return applicable_services

def evaluate_rule_group(rule_group, order):
    """
    Evaluate a rule group against an order.
    """
    rules = rule_group.rules.all()

    if rule_group.logic_operator == 'AND':
        return all(evaluate_rule(rule, order) for rule in rules)
    elif rule_group.logic_operator == 'OR':
        return any(evaluate_rule(rule, order) for rule in rules)
    elif rule_group.logic_operator == 'NOT':
        return not any(evaluate_rule(rule, order) for rule in rules)
    elif rule_group.logic_operator == 'XOR':
        return sum(evaluate_rule(rule, order) for rule in rules) == 1
    elif rule_group.logic_operator == 'NAND':
        return not all(evaluate_rule(rule, order) for rule in rules)
    elif rule_group.logic_operator == 'NOR':
        return not any(evaluate_rule(rule, order) for rule in rules)
    else:
        raise ValueError(f"Unsupported logic operator: {rule_group.logic_operator}")

def evaluate_rule(rule, order):
    """
    Evaluate a single rule against an order.
    """
    order_value = getattr(order, rule.field, None)

    if order_value is None:
        return False

    if rule.field == 'sku_quantity':
        return evaluate_sku_quantity_rule(rule, order_value)

    if rule.operator in ['gt', 'lt', 'ge', 'le', 'eq', 'ne']:
        return evaluate_numeric_rule(rule, order_value)

    if rule.operator in ['in', 'ni', 'contains', 'ncontains', 'startswith', 'endswith']:
        return evaluate_string_rule(rule, str(order_value))

    raise ValueError(f"Unsupported operator: {rule.operator}")

def evaluate_sku_quantity_rule(rule, order_value):
    if rule.operator == 'contains':
        return rule.value in order_value.keys()
    elif rule.operator == 'eq':
        try:
            return order_value == json.loads(rule.value)
        except json.JSONDecodeError:
            return False
    elif rule.operator in ['in', 'ni']:
        values = rule.get_values_as_list()
        if rule.operator == 'in':
            return any(item in order_value.keys() for item in values)
        else:  # 'ni'
            return all(item not in order_value.keys() for item in values)
    return False

def evaluate_numeric_rule(rule, order_value):
    try:
        numeric_value = float(rule.value)
        order_numeric = float(order_value)
    except ValueError:
        return False

    if rule.operator == 'gt':
        return order_numeric > numeric_value
    elif rule.operator == 'lt':
        return order_numeric < numeric_value
    elif rule.operator == 'ge':
        return order_numeric >= numeric_value
    elif rule.operator == 'le':
        return order_numeric <= numeric_value
    elif rule.operator == 'eq':
        return order_numeric == numeric_value
    elif rule.operator == 'ne':
        return order_numeric != numeric_value

    return False

def evaluate_string_rule(rule, order_value):
    if rule.operator == 'in':
        return order_value in rule.get_values_as_list()
    elif rule.operator == 'ni':
        return order_value not in rule.get_values_as_list()
    elif rule.operator == 'contains':
        return rule.value in order_value
    elif rule.operator == 'ncontains':
        return rule.value not in order_value
    elif rule.operator == 'startswith':
        return order_value.startswith(rule.value)
    elif rule.operator == 'endswith':
        return order_value.endswith(rule.value)

    return False