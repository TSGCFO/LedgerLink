import os
import django
from datetime import datetime, timezone
import json

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'LedgerLink.settings')
django.setup()

from orders.models import Order
from customer_services.models import CustomerService
from services.models import Service
from rules.models import RuleGroup, Rule

def check_b2b_orders():
    """Check for orders that should match the B2B Base service rule criteria"""
    
    # Get the time period
    start = datetime(2024, 2, 16, tzinfo=timezone.utc)
    end = datetime(2024, 3, 6, 23, 59, 59, 999999, tzinfo=timezone.utc)
    
    # Get the B2B Base service
    b2b_base_service = Service.objects.get(service_name='B2B Base')
    print(f"B2B Base service ID: {b2b_base_service.id}")
    
    # Get customer service for Abokichi
    customer_services = CustomerService.objects.filter(service=b2b_base_service)
    print(f"Customer services for B2B Base: {customer_services.count()}")
    
    for cs in customer_services:
        print(f"Customer Service ID: {cs.id}, Customer ID: {cs.customer_id}")
        
        # Get rule groups for this customer service
        rule_groups = RuleGroup.objects.filter(customer_service_id=cs.id)
        
        for rg in rule_groups:
            print(f"Rule group {rg.id}: Logic operator={rg.logic_operator}")
            
            # Get rules
            rules = Rule.objects.filter(rule_group=rg)
            for rule in rules:
                print(f"  - Rule: Field={rule.field}, Operator={rule.operator}, Value={rule.value}")
            
            # Now check for orders that match these rules
            # From the previous investigation, we know we're looking for:
            # - reference_number startswith "INV"
            # - notes eq "wholesale"
            
            # Direct query for orders matching the criteria
            orders = Order.objects.filter(
                close_date__gte=start,
                close_date__lte=end,
                reference_number__startswith="INV",
                notes="wholesale"
            )
            
            print(f"\nOrders matching B2B Base criteria in period: {orders.count()}")
            
            # Show some details of the first 5 matching orders
            for order in orders[:5]:
                print(f"  Order Ref: {order.reference_number}, Notes: {order.notes}")
            
            # If no orders found with exact criteria, let's loosen it to see why
            if orders.count() == 0:
                print("\nChecking with relaxed criteria:")
                
                # Check just for reference numbers starting with INV
                inv_orders = Order.objects.filter(
                    close_date__gte=start,
                    close_date__lte=end,
                    reference_number__startswith="INV"
                )
                print(f"Orders with reference_number starting with 'INV': {inv_orders.count()}")
                
                # Show some examples
                for order in inv_orders[:5]:
                    print(f"  Order Ref: {order.reference_number}, Notes: {order.notes}")
                
                # Check just for notes = "wholesale"
                wholesale_orders = Order.objects.filter(
                    close_date__gte=start,
                    close_date__lte=end,
                    notes="wholesale"
                )
                print(f"Orders with notes='wholesale': {wholesale_orders.count()}")
                
                # Show some examples
                for order in wholesale_orders[:5]:
                    print(f"  Order Ref: {order.reference_number}, Notes: {order.notes}")
                
                # Check for similar but not exact notes
                similar_notes_orders = Order.objects.filter(
                    close_date__gte=start,
                    close_date__lte=end,
                    notes__icontains="wholesale"
                )
                print(f"Orders with notes containing 'wholesale': {similar_notes_orders.count()}")
                
                # Show some examples
                for order in similar_notes_orders[:5]:
                    print(f"  Order Ref: {order.reference_number}, Notes: {order.notes}")
            
            # Now check for any service costs generated for B2B Base
            from Billing_V2.models import ServiceCost, OrderCost
            
            # Check order costs for these orders
            order_costs = OrderCost.objects.filter(
                order__close_date__gte=start,
                order__close_date__lte=end
            )
            print(f"\nTotal order costs in period: {order_costs.count()}")
            
            # Check for B2B Base costs
            b2b_costs = ServiceCost.objects.filter(
                service_id=b2b_base_service.id,
                order_cost__in=order_costs
            )
            print(f"B2B Base service costs in period: {b2b_costs.count()}")
            
            # Compare directly with the rule evaluator
            from Billing_V2.utils.calculator import RuleEvaluator
            
            # Manual evaluation of a few orders - do they match the rule?
            print("\nManual rule evaluation of sample orders:")
            
            # Sample some orders
            sample_orders = Order.objects.filter(close_date__gte=start, close_date__lte=end)[:10]
            
            for order in sample_orders:
                # Create a rule evaluator and evaluate the rule group
                evaluator = RuleEvaluator()
                
                # Evaluate the rule group rules on this order
                match = True
                for rule in rules:
                    rule_match = evaluator.evaluate_rule(rule, order)
                    if not rule_match:
                        match = False
                        break
                
                print(f"Order (Ref: {order.reference_number}, Notes: {order.notes}): {'MATCH' if match else 'NO MATCH'}")

if __name__ == "__main__":
    check_b2b_orders()