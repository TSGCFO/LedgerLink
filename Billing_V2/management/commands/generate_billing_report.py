import os
import json
import logging
import sys
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.db import transaction
from customers.models import Customer
from ...utils.calculator import generate_billing_report

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Generate billing reports for customers'

    def add_arguments(self, parser):
        # Required arguments
        parser.add_argument('--customer-id', type=int, help='Customer ID to generate report for')
        
        # Optional arguments
        parser.add_argument('--all-customers', action='store_true', 
                            help='Generate reports for all active customers')
        parser.add_argument('--start-date', type=str, 
                            help='Start date (YYYY-MM-DD) for report period')
        parser.add_argument('--end-date', type=str, 
                            help='End date (YYYY-MM-DD) for report period')
        parser.add_argument('--days', type=int, default=30, 
                            help='Number of days for report period (default: 30)')
        parser.add_argument('--output-format', type=str, choices=['json', 'csv', 'dict'], 
                            default='json', help='Output format for reports')
        parser.add_argument('--output-dir', type=str, 
                            help='Directory to save report files')

    def handle(self, *args, **options):
        # Parse options
        customer_id = options.get('customer_id')
        all_customers = options.get('all_customers')
        start_date = options.get('start_date')
        end_date = options.get('end_date')
        days = options.get('days')
        output_format = options.get('output_format')
        output_dir = options.get('output_dir')
        
        # Validate options
        if not customer_id and not all_customers:
            raise CommandError('You must specify either --customer-id or --all-customers')
            
        if customer_id and all_customers:
            raise CommandError('You cannot specify both --customer-id and --all-customers')
            
        # Parse dates
        if start_date:
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d')
            except ValueError:
                raise CommandError('Invalid start date format. Use YYYY-MM-DD')
        else:
            # Default to days ago from now or yesterday
            start_date = timezone.now() - timedelta(days=days)
            
        if end_date:
            try:
                end_date = datetime.strptime(end_date, '%Y-%m-%d')
            except ValueError:
                raise CommandError('Invalid end date format. Use YYYY-MM-DD')
        else:
            # Default to yesterday
            end_date = timezone.now() - timedelta(days=1)
            
        # Validate date range
        if start_date > end_date:
            raise CommandError('Start date must be before end date')
            
        # Create output directory if needed
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        # Get customers
        if all_customers:
            customers = Customer.objects.filter(is_active=True)
            self.stdout.write(f'Generating reports for {customers.count()} active customers')
        else:
            try:
                customers = [Customer.objects.get(id=customer_id)]
                self.stdout.write(f'Generating report for customer {customer_id}')
            except Customer.DoesNotExist:
                raise CommandError(f'Customer with ID {customer_id} not found')
                
        # Generate reports
        reports = []
        for customer in customers:
            try:
                self.stdout.write(f'Processing customer: {customer.company_name} (ID: {customer.id})')
                
                # Generate report
                report_data = generate_billing_report(
                    customer_id=customer.id,
                    start_date=start_date,
                    end_date=end_date,
                    output_format=output_format
                )
                
                # Save to file if output directory specified
                if output_dir:
                    file_date = start_date.strftime('%Y%m%d')
                    
                    if output_format == 'json':
                        filename = f'billing_report_{customer.id}_{file_date}.json'
                        file_path = os.path.join(output_dir, filename)
                        with open(file_path, 'w') as f:
                            f.write(report_data)
                    elif output_format == 'csv':
                        filename = f'billing_report_{customer.id}_{file_date}.csv'
                        file_path = os.path.join(output_dir, filename)
                        with open(file_path, 'w') as f:
                            f.write(report_data)
                    elif output_format == 'dict':
                        filename = f'billing_report_{customer.id}_{file_date}.json'
                        file_path = os.path.join(output_dir, filename)
                        with open(file_path, 'w') as f:
                            json.dump(report_data, f, indent=2)
                            
                    self.stdout.write(f'Report saved to {file_path}')
                
                # Track report data
                if isinstance(report_data, dict):
                    reports.append(report_data)
                elif output_format == 'json':
                    try:
                        reports.append(json.loads(report_data))
                    except json.JSONDecodeError:
                        reports.append({'customer_id': customer.id, 'error': 'Invalid JSON data'})
                        
                self.stdout.write(self.style.SUCCESS(f'Successfully generated report for {customer.company_name}'))
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error generating report for {customer.company_name}: {str(e)}'))
                
        # Print summary
        self.stdout.write(f'Generated {len(reports)} reports')
        for report in reports:
            if isinstance(report, dict) and 'total_amount' in report:
                self.stdout.write(f'Customer {report.get("customer_name", report.get("customer_id"))}: '
                                 f'${report["total_amount"]:.2f}')
                
        self.stdout.write(self.style.SUCCESS('Done'))
