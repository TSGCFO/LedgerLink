import os
import sys
import django
from datetime import datetime

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'LedgerLink.settings')
django.setup()

# Import models
from customers.models import Customer
from Billing_V2.utils.calculator import BillingCalculator

def main():
    # Get customer
    customer = Customer.objects.first()
    if not customer:
        print("No customers found in database")
        return
    
    print(f"Testing report generation for customer: {customer.company_name} (ID: {customer.id})")
    
    # Set date range
    start_date = datetime(2024, 2, 16)
    end_date = datetime(2024, 3, 10)
    
    # Generate report
    try:
        calculator = BillingCalculator(
            customer_id=customer.id,
            start_date=start_date,
            end_date=end_date
        )
        
        # Validate input
        calculator.validate_input()
        
        # Generate the report
        report = calculator.generate_report()
        
        # Print report data
        print(f"Generated report ID: {report.id}")
        print(f"Total amount: ${report.total_amount}")
        print(f"Order count: {report.order_costs.count()}")
        print(f"Service totals: {report.service_totals}")
        
        print("\nReport generation successful!")
        
    except Exception as e:
        print(f"Error generating report: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()