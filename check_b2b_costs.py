import os
import django
from datetime import datetime, timezone
import json

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'LedgerLink.settings')
django.setup()

from Billing_V2.models import ServiceCost, OrderCost
from rules.models import RuleGroup
from customer_services.models import CustomerService

def check_b2b_base_service():
    # Check the rule groups for B2B Base service
    cs = CustomerService.objects.get(id=32)  # B2B Base for Abokichi
    rule_groups = RuleGroup.objects.filter(customer_service_id=cs.id)
    
    print(f"Rule groups for B2B Base service (id=32): {rule_groups.count()}")
    
    # Print rule details
    for rg in rule_groups:
        print(f"Rule group {rg.id}: Logic operator={rg.logic_operator}, Rules count={rg.rules.count()}")
        
        for rule in rg.rules.all():
            print(f"  - Field: {rule.field}, Operator: {rule.operator}, Value: {rule.value}, Adjustment: {rule.adjustment_amount}")
    
    # Check if B2B Base service has costs in the test period
    start = datetime(2024, 2, 16, tzinfo=timezone.utc)
    end = datetime(2024, 3, 6, 23, 59, 59, 999999, tzinfo=timezone.utc)
    
    # First get the order costs for the period
    from orders.models import Order
    # Use close_date instead of date based on error message showing available fields
    orders_in_period = Order.objects.filter(close_date__gte=start, close_date__lte=end)
    print(f"\nOrders in period: {orders_in_period.count()}")
    
    # Now get order costs related to these orders
    order_costs = OrderCost.objects.filter(order__in=orders_in_period)
    print(f"Order costs for these orders: {order_costs.count()}")
    
    # Finally get the B2B Base service costs
    b2b_base_costs = ServiceCost.objects.filter(
        service_id=1,
        order_cost__in=order_costs
    )
    
    print(f"\nB2B Base (service_id=1) costs in period: {b2b_base_costs.count()}")
    
    if b2b_base_costs.count() > 0:
        # Convert to list and then to dict for easier serialization
        costs = []
        for cost in b2b_base_costs[:5]:  # Get first 5 for example
            costs.append({
                'id': cost.id,
                'service_id': cost.service_id,
                'service_name': cost.service_name,
                'amount': float(cost.amount),
                'order_cost_id': cost.order_cost_id
            })
        print(f"First few costs: {json.dumps(costs, indent=2)}")
    
    # Count total amount for B2B Base service in the period
    total_amount = sum(cost.amount for cost in b2b_base_costs)
    print(f"Total amount for B2B Base service in period: {total_amount}")
    
    # Check if the issue is with filtering
    print("\nChecking filter behavior:")
    
    # The incorrect filter used in the original code
    wrong_filter_groups = RuleGroup.objects.filter(
        customer_service__in=[cs.id]
    ).select_related('customer_service')
    
    print(f"Rule groups found using customer_service__in=[cs.id]: {wrong_filter_groups.count()}")
    
    # The correct filter that should fix the issue
    correct_filter_groups = RuleGroup.objects.filter(
        customer_service_id__in=[cs.id]
    ).select_related('customer_service')
    
    print(f"Rule groups found using customer_service_id__in=[cs.id]: {correct_filter_groups.count()}")

if __name__ == "__main__":
    check_b2b_base_service()