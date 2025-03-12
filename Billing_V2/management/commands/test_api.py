"""
Management command to test Billing V2 API endpoints directly.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import json
from Billing_V2.utils.calculator import BillingCalculator
from Billing_V2.serializers import BillingReportRequestSerializer

class Command(BaseCommand):
    help = 'Test the Billing V2 API endpoints'
    
    def handle(self, *args, **options):
        # Test data
        today = timezone.now()
        start_date = today - timedelta(days=30)
        end_date = today
        
        self.stdout.write(self.style.SUCCESS('Testing BillingCalculator directly'))
        self.stdout.write('=' * 80)
        
        try:
            # Test serializer
            data = {
                'customer_id': 1,
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d'),
                'output_format': 'json'
            }
            
            self.stdout.write(f"Testing data: {json.dumps(data, indent=2)}")
            serializer = BillingReportRequestSerializer(data=data)
            
            if serializer.is_valid():
                self.stdout.write(self.style.SUCCESS("Serializer validation passed"))
                validated_data = serializer.validated_data
                self.stdout.write(f"Validated data: {validated_data}")
            else:
                self.stdout.write(self.style.ERROR(f"Serializer validation failed: {serializer.errors}"))
                return
                
            # Test calculator directly
            calculator = BillingCalculator(
                customer_id=validated_data['customer_id'],
                start_date=validated_data['start_date'],
                end_date=validated_data['end_date']
            )
            
            self.stdout.write("Generating report with calculator...")
            report = calculator.generate_report()
            self.stdout.write(self.style.SUCCESS("Report generated successfully"))
            
            # Output report details
            self.stdout.write(f"Report ID: {report.id}")
            self.stdout.write(f"Report customer ID: {report.customer_id}")
            self.stdout.write(f"Report total amount: {report.total_amount}")
            self.stdout.write(f"Report date range: {report.start_date} to {report.end_date}")
            self.stdout.write(f"Report order costs count: {report.order_costs.count()}")
            self.stdout.write(f"Report service totals: {json.dumps(report.service_totals, indent=2)}")
            
            # Test JSON serialization
            self.stdout.write("Testing JSON serialization...")
            json_data = calculator.to_json()
            self.stdout.write(self.style.SUCCESS("JSON serialization successful"))
            
            # Test CSV serialization
            self.stdout.write("Testing CSV serialization...")
            csv_data = calculator.to_csv()
            self.stdout.write(self.style.SUCCESS("CSV serialization successful"))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error testing BillingCalculator: {str(e)}"))
