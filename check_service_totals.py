import os
import django
from datetime import datetime, timezone
import json

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'LedgerLink.settings')
django.setup()

from Billing_V2.models import ServiceCost, OrderCost
from orders.models import Order
from services.models import Service
from customer_services.models import CustomerService
from rules.models import RuleGroup

def check_all_services():
    # Define the test period
    start = datetime(2024, 2, 16, tzinfo=timezone.utc)
    end = datetime(2024, 3, 6, 23, 59, 59, 999999, tzinfo=timezone.utc)
    
    # Get orders in the period
    orders = Order.objects.filter(close_date__gte=start, close_date__lte=end)
    print(f"Orders in period: {orders.count()}")
    
    # Get service costs for these orders
    costs = ServiceCost.objects.filter(order_cost__order__in=orders)
    print(f"Total service costs: {costs.count()}")
    
    # Group and sum by service ID
    service_totals = {}
    for cost in costs:
        sid = cost.service_id
        if sid not in service_totals:
            service_totals[sid] = {
                'name': cost.service_name,
                'count': 0,
                'amount': 0
            }
        service_totals[sid]['count'] += 1
        service_totals[sid]['amount'] += float(cost.amount)
    
    # Display services with billable amounts
    print("\nServices with billable amounts in the period:")
    print("---------------------------------------------")
    for sid, data in service_totals.items():
        print(f"Service ID: {sid}, Name: {data['name']}")
        print(f"  - Record count: {data['count']}")
        print(f"  - Total amount: {data['amount']}")
    
    # Get details about the rule groups for each service
    print("\nRule group details:")
    print("------------------")
    
    # Get all service IDs from the costs
    service_ids = list(service_totals.keys())
    
    # Get the customer services for these service IDs
    customer_services = CustomerService.objects.filter(service_id__in=service_ids)
    for cs in customer_services:
        print(f"Service ID: {cs.service_id}, Customer ID: {cs.customer_id}")
        
        # Check both filter methods and compare results
        using_in = RuleGroup.objects.filter(customer_service__in=[cs.id]).count()
        using_id_in = RuleGroup.objects.filter(customer_service_id__in=[cs.id]).count()
        
        print(f"  - Rule groups (customer_service__in): {using_in}")
        print(f"  - Rule groups (customer_service_id__in): {using_id_in}")
        print(f"  - Difference: {using_id_in - using_in}")
    
    # Now specifically check B2B Base (service_id=1)
    print("\nB2B Base Service Check:")
    print("---------------------")
    
    # Get customer services for B2B Base
    b2b_services = CustomerService.objects.filter(service_id=1)
    print(f"Customer services for B2B Base: {b2b_services.count()}")
    
    for cs in b2b_services:
        print(f"Customer Service ID: {cs.id}, Customer ID: {cs.customer_id}")
        
        # Check rule groups
        rule_groups = RuleGroup.objects.filter(customer_service_id=cs.id)
        print(f"  - Rule groups: {rule_groups.count()}")
        
        # Count B2B Base costs for this customer
        customer_costs = ServiceCost.objects.filter(
            service_id=1, 
            order_cost__order__in=orders,
            order_cost__order__customer_id=cs.customer_id
        )
        print(f"  - Service costs: {customer_costs.count()}")
        
        # Sum the costs
        total = sum(float(cost.amount) for cost in customer_costs)
        print(f"  - Total amount: {total}")

if __name__ == "__main__":
    print("Checking services with billable amounts in the test period...")
    check_all_services()