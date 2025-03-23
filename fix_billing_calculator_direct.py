# Fix for billing calculator service filter issue

import os
import django
import json
from datetime import datetime, date
from decimal import Decimal
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'LedgerLink.settings')
django.setup()

from customers.models import Customer
from Billing_V2.utils.calculator import BillingCalculator
from customer_services.models import CustomerService
from services.models import Service
from Billing_V2.models import BillingReport
from rules.models import RuleGroup

def test_billing_calculator_fix():
    """
    Test that the billing calculator correctly filters by specific service when selected
    
    The issue was in the BillingCalculator class where rule groups were filtered
    using customer_service__in instead of customer_service_id__in when specific
    services are selected. This caused the filter to look for rule groups where
    the entire customer_service object was in the list, rather than filtering by ID.
    """
    logger.info("Testing the billing calculator fix...")
    
    # Get Abokichi customer
    customer = Customer.objects.filter(company_name='Abokichi').first()
    if not customer:
        logger.error("Abokichi customer not found")
        return
    
    # Get B2B Base service
    b2b_base_service = Service.objects.filter(service_name='B2B Base').first()
    if not b2b_base_service:
        logger.error("B2B Base service not found")
        return
    
    # Get B2B Base customer service for Abokichi
    b2b_base_cs = CustomerService.objects.filter(
        customer=customer,
        service=b2b_base_service
    ).first()
    
    if not b2b_base_cs:
        logger.error("B2B Base customer service not found for Abokichi")
        return
    
    logger.info(f"Found B2B Base customer service ID: {b2b_base_cs.id}")
    
    # Verify rule groups for B2B Base service with correct filter
    rule_groups = RuleGroup.objects.filter(customer_service_id__in=[b2b_base_cs.id])
    logger.info(f"Found {rule_groups.count()} rule groups for B2B Base service using customer_service_id__in")
    
    # Also check the old incorrect filter method for comparison
    rule_groups_old_method = RuleGroup.objects.filter(customer_service__in=[b2b_base_cs.id])
    logger.info(f"Found {rule_groups_old_method.count()} rule groups using incorrect customer_service__in")
    
    # Create dates for test
    start_date = date(2024, 2, 16)
    end_date = date(2024, 3, 6)
    
    # Test with all services
    logger.info("\nTEST 1: Creating report with ALL SERVICES")
    all_services_calc = BillingCalculator(
        customer_id=customer.id,
        start_date=start_date,
        end_date=end_date,
        customer_service_ids=None  # None = all services
    )
    
    all_services_report = all_services_calc.generate_report()
    logger.info(f"All services report total: {all_services_report.total_amount}")
    
    # Test with B2B Base service only
    logger.info("\nTEST 2: Creating report with ONLY B2B BASE SERVICE")
    specific_service_calc = BillingCalculator(
        customer_id=customer.id,
        start_date=start_date,
        end_date=end_date,
        customer_service_ids=[b2b_base_cs.id]  # Just B2B Base service
    )
    
    specific_service_report = specific_service_calc.generate_report()
    logger.info(f"B2B Base only report total: {specific_service_report.total_amount}")
    
    # Get B2B Base amount in all services report
    b2b_base_service_id = str(b2b_base_service.id)
    b2b_base_amount_in_all = 0
    
    if b2b_base_service_id in all_services_report.service_totals:
        b2b_base_amount_in_all = float(all_services_report.service_totals[b2b_base_service_id]['amount'])
    
    logger.info(f"\nCOMPARISON:")
    logger.info(f"B2B Base amount in All services report: {b2b_base_amount_in_all}")
    logger.info(f"B2B Base amount in B2B Base only report: {float(specific_service_report.total_amount) if specific_service_report.total_amount else 0}")
    
    # Explain what the fix did
    logger.info("\nEXPLANATION OF THE FIX:")
    logger.info("The issue was in the BillingCalculator class in calculator.py line 246-247:")
    logger.info("Original code was using: customer_service__in=[cs.id for cs in customer_services]")
    logger.info("Fixed code now uses: customer_service_id__in=[cs.id for cs in customer_services]")
    logger.info("The fix ensures that the filter correctly matches rule groups by customer service IDs")
    
    # Check if the fix worked
    if specific_service_report.total_amount > 0:
        logger.info("SUCCESS: B2B Base service now shows a total when selected individually")
        logger.info("The billing calculator fix is working correctly!")
    elif b2b_base_amount_in_all == 0:
        logger.info("TEST INCONCLUSIVE: No billable amount for B2B Base service in this period for either method")
    else:
        logger.error(f"ISSUE REMAINS: B2B Base has value {b2b_base_amount_in_all} in all services but {specific_service_report.total_amount} when selected individually")

if __name__ == "__main__":
    logger.info("Testing the billing calculator service filter fix")
    test_billing_calculator_fix()