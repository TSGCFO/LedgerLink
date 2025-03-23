import os
import sys
import django
from datetime import datetime, date
from decimal import Decimal
import json
import logging

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'LedgerLink.settings')
django.setup()

from customers.models import Customer
from Billing_V2.utils.calculator import BillingCalculator
from customer_services.models import CustomerService
from services.models import Service
from Billing_V2.models import BillingReport
from django.db import connection

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_diagnostic_test():
    """
    Run diagnostic tests to identify why specific service selection returns zero totals
    """
    # Use specific customer as mentioned by user
    customer = Customer.objects.filter(company_name='Abokichi').first()
    if not customer:
        logger.error("Abokichi customer not found in the database")
        return

    # Get customer services
    services = CustomerService.objects.filter(customer=customer)
    if not services:
        logger.error(f"No services found for customer {customer.id} ({customer.company_name})")
        return

    logger.info(f"Found customer {customer.id} ({customer.company_name}) with {services.count()} services")

    # Use specific date range mentioned by user
    start_date = date(2024, 2, 16)
    end_date = date(2024, 3, 5)
    
    logger.info(f"Using date range: {start_date} to {end_date}")

    # Test case 1: All services
    logger.info("TEST CASE 1: ALL SERVICES")
    all_services_calc = BillingCalculator(
        customer_id=customer.id,
        start_date=start_date,
        end_date=end_date,
        customer_service_ids=None  # None = all services
    )

    # Get details about rule groups
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT cs.id, cs.service_id, s.service_name, COUNT(rg.id) 
            FROM customer_services_customerservice cs
            JOIN services_service s ON cs.service_id = s.id
            LEFT JOIN rules_rulegroup rg ON rg.customer_service_id = cs.id
            WHERE cs.customer_id = %s
            GROUP BY cs.id, cs.service_id, s.service_name
        """, [customer.id])
        
        logger.info("Service ID | Service Name | Rule Group Count")
        for row in cursor.fetchall():
            logger.info(f"{row[0]} | {row[2]} | {row[3]}")
    
    # Generate report with all services
    try:
        all_services_report = all_services_calc.generate_report()
        logger.info(f"All services report total: {all_services_report.total_amount}")
        
        # Convert decimal values to float for pretty printing
        service_totals_dict = {}
        for service_id, data in all_services_report.service_totals.items():
            service_totals_dict[service_id] = {
                'service_name': data['service_name'],
                'amount': float(data['amount'])
            }
        
        logger.info(f"Service totals: {json.dumps(service_totals_dict, indent=2)}")
    except Exception as e:
        logger.error(f"Error generating all services report: {str(e)}")
        return

    # Test case 2: Specific B2B Base service as mentioned by user
    logger.info("\nTEST CASE 2: SPECIFIC SERVICE (B2B Base)")
    
    # Find the B2B Base customer service
    b2b_base_service = Service.objects.filter(service_name='B2B Base').first()
    if not b2b_base_service:
        logger.error("B2B Base service not found")
        return
    
    b2b_base_cs = CustomerService.objects.filter(
        customer=customer, 
        service=b2b_base_service
    ).first()
    
    if not b2b_base_cs:
        logger.error("B2B Base customer service not found for Abokichi")
        return
    
    logger.info(f"Found B2B Base customer service ID: {b2b_base_cs.id}")
    
    specific_services_calc = BillingCalculator(
        customer_id=customer.id,
        start_date=start_date,
        end_date=end_date,
        customer_service_ids=[b2b_base_cs.id]  # Just the B2B Base service
    )
    
    # Generate report with B2B Base service only
    try:
        specific_services_report = specific_services_calc.generate_report()
        logger.info(f"B2B Base service report total: {specific_services_report.total_amount}")
        
        # Convert decimal values to float for pretty printing
        specific_service_totals_dict = {}
        for service_id, data in specific_services_report.service_totals.items():
            specific_service_totals_dict[service_id] = {
                'service_name': data['service_name'],
                'amount': float(data['amount'])
            }
        
        logger.info(f"Service totals: {json.dumps(specific_service_totals_dict, indent=2)}")
    except Exception as e:
        logger.error(f"Error generating specific service report: {str(e)}")
        return
    
    # Compare results
    logger.info("\nCOMPARISON")
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
    logger.info(f"B2B Base amount in B2B Base only report: {float(specific_total) if specific_total else 0}")
    
    if specific_total == 0 and b2b_base_amount_in_all > 0:
        logger.error("ISSUE CONFIRMED: B2B Base service returns zero total when selected specifically, but has costs when all services are selected")
        
        # Diagnose the issue further by looking at how rule groups are processed
        logger.info("\nDIAGNOSING RULE GROUPS")
        
        # Get rule groups for B2B Base service
        from rules.models import RuleGroup
        
        rule_groups = RuleGroup.objects.filter(customer_service=b2b_base_cs)
        logger.info(f"Rule groups for B2B Base service: {rule_groups.count()}")
        
        for rg in rule_groups:
            logger.info(f"Rule group {rg.id}: {rg.logic_operator}, Rules count: {rg.rules.count()}")
            
        # Check how rule groups are fetched in BillingCalculator for specific services
        logger.info("\nDIAGNOSING SERVICE FILTERING IN CALCULATOR")
        
        # What the current code does for rule group filtering:
        customer_services_query = CustomerService.objects.filter(
            customer_id=customer.id
        )
        all_services_list = list(customer_services_query.select_related('service'))
        filtered_services = [cs for cs in all_services_list if cs.id == b2b_base_cs.id]
        
        rule_groups = RuleGroup.objects.filter(
            customer_service__in=[cs.id for cs in filtered_services]
        ).select_related('customer_service')
        
        logger.info(f"Rule groups found using customer_service__in filter: {rule_groups.count()}")
        
        # Test alternate filtering approach
        alt_rule_groups = RuleGroup.objects.filter(
            customer_service_id__in=[cs.id for cs in filtered_services]
        )
        
        logger.info(f"Rule groups found using customer_service_id__in filter: {alt_rule_groups.count()}")
        
        # Compare results
        if rule_groups.count() != alt_rule_groups.count():
            logger.error(f"POSSIBLE CAUSE FOUND: Different number of rule groups returned by different filter methods")
            logger.info(f"This suggests that using customer_service__in=[cs.id for cs in filtered_services] is not working as expected")

if __name__ == '__main__':
    logger.info("Running billing calculator diagnostic with specific test case")
    run_diagnostic_test()