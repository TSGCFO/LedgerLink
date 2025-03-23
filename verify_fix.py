import os
import django
from datetime import datetime, timezone
import json
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'LedgerLink.settings')
django.setup()

from Billing_V2.models import ServiceCost, OrderCost, BillingReport
from Billing_V2.utils.calculator import BillingCalculator
from orders.models import Order
from customer_services.models import CustomerService
from services.models import Service
from rules.models import RuleGroup, Rule
from customers.models import Customer
from Billing_V2.utils.rule_evaluator import RuleEvaluator

# Monkey patch the RuleGroup.evaluate method to ensure it uses our improved rule evaluator
original_evaluate = RuleGroup.evaluate

def patched_evaluate(self, order):
    """Monkey-patched version of RuleGroup.evaluate to use static RuleEvaluator method"""
    logger.info(f"Using patched rule group evaluation for group {self.id}")
    
    rules = list(self.rules.all().select_related())
    if not rules:
        return True
    
    # Use the static method directly instead of creating a new instance
    results = [RuleEvaluator.evaluate_rule(rule, order) for rule in rules]
    
    if self.logic_operator == 'AND':
        return all(results)
    elif self.logic_operator == 'OR':
        return any(results)
    elif self.logic_operator == 'NOT':
        return not any(results)
    elif self.logic_operator == 'XOR':
        return results.count(True) == 1
    elif self.logic_operator == 'NAND':
        return not all(results)
    elif self.logic_operator == 'NOR':
        return not any(results)
    else:
        logger.warning(f"Unknown logic operator {self.logic_operator}")
        return False

# Apply the monkey patch
RuleGroup.evaluate = patched_evaluate

def verify_filtering_fix():
    """
    Verify the fix for the billing calculator service selection issue
    """
    logger.info("Starting verification of billing calculator service selection fix")
    
    # Use the same time period as our earlier tests
    start_date = datetime(2024, 2, 16, tzinfo=timezone.utc)
    end_date = datetime(2024, 3, 6, 23, 59, 59, 999999, tzinfo=timezone.utc)
    
    # Get Abokichi customer
    customer = Customer.objects.get(id=1)
    
    # Get B2B Base service
    b2b_base_service = Service.objects.get(service_name='B2B Base')
    logger.info(f"B2B Base service ID: {b2b_base_service.id}")
    
    # Get B2B Base customer service
    b2b_base_cs = CustomerService.objects.filter(
        customer=customer, 
        service=b2b_base_service
    ).first()
    
    if not b2b_base_cs:
        logger.error("B2B Base customer service not found for Abokichi")
        return
    
    logger.info(f"Found B2B Base customer service ID: {b2b_base_cs.id}")
    
    # Get rule groups for B2B Base service to understand what we're looking for
    rule_groups = RuleGroup.objects.filter(customer_service=b2b_base_cs)
    logger.info(f"Rule groups for B2B Base service: {rule_groups.count()}")
    
    for rg in rule_groups:
        logger.info(f"Rule group {rg.id}: {rg.logic_operator}")
        for rule in rg.rules.all():
            logger.info(f"  - Rule: Field={rule.field}, Operator={rule.operator}, Value={rule.value}")
    
    # 1. Create test order that matches B2B Base criteria
    test_order = create_test_order(customer)
    logger.info(f"Created test order with Ref: {test_order.reference_number}, Notes: {test_order.notes}")
    
    # 2. Test with "All services" selection
    all_services_calc = BillingCalculator(
        customer_id=customer.id,
        start_date=start_date,
        end_date=end_date
    )
    
    # Generate report with all services
    all_services_report = all_services_calc.generate_report()
    logger.info(f"All services report total: {all_services_report.total_amount}")
    
    # 3. Test with specific service selection (B2B Base only)
    specific_services_calc = BillingCalculator(
        customer_id=customer.id,
        start_date=start_date,
        end_date=end_date,
        customer_service_ids=[b2b_base_cs.id]  # Just the B2B Base service
    )
    
    # Generate report with B2B Base service only
    specific_services_report = specific_services_calc.generate_report()
    logger.info(f"B2B Base service report total: {specific_services_report.total_amount}")
    
    # 4. Compare results
    logger.info("\nCOMPARISON AFTER FIX")
    all_total = all_services_report.total_amount
    specific_total = specific_services_report.total_amount
    
    logger.info(f"All services total: {all_total}")
    logger.info(f"B2B Base service total: {specific_total}")
    
    # Find the B2B Base service amount in the all services report
    b2b_base_service_id = str(b2b_base_service.id)
    b2b_base_amount_in_all = 0
    
    if b2b_base_service_id in all_services_report.service_totals:
        b2b_base_amount_in_all = float(all_services_report.service_totals[b2b_base_service_id]['amount'])
    
    logger.info(f"B2B Base amount in All services report: {b2b_base_amount_in_all}")
    
    # Clean up test order
    delete_test_order(test_order)
    
    # Check result
    if b2b_base_amount_in_all > 0 and specific_total > 0:
        logger.info("VERIFICATION SUCCESSFUL: Both reports show B2B Base service with billable amount")
        if abs(b2b_base_amount_in_all - float(specific_total)) < 0.01:
            logger.info("AMOUNTS MATCH: The B2B Base amount is the same in both reports")
        else:
            logger.warning(f"AMOUNTS DIFFER: All services: {b2b_base_amount_in_all}, Specific: {float(specific_total)}")
    else:
        logger.error("VERIFICATION FAILED: One or both reports show zero for B2B Base service")

def create_test_order(customer):
    """Create a test order that matches the B2B Base criteria"""
    # Create an order that matches the B2B Base rule criteria
    # (reference_number starts with INV and notes equals wholesale)
    # Use a date within the test period (Feb 16 to Mar 6, 2024)
    test_date = datetime(2024, 2, 20, tzinfo=timezone.utc)
    
    order = Order.objects.create(
        customer=customer,
        reference_number='INV-TEST-1234',
        notes='WHOLESALE',  # Use uppercase to test case-insensitive matching
        close_date=test_date,  # Within the date range being calculated
        transaction_id=str(int(datetime.now().timestamp())),  # Numeric transaction ID
        status='delivered'  # Valid status options: draft, submitted, shipped, delivered, cancelled
    )
    return order

def delete_test_order(order):
    """Delete the test order"""
    order.delete()
    logger.info(f"Deleted test order")

if __name__ == "__main__":
    logger.info("Verifying billing calculator service selection fix")
    verify_filtering_fix()