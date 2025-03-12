import os
import csv
import json
import logging
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.db.models import Q
from ...models import BillingReport

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Export billing reports in bulk'

    def add_arguments(self, parser):
        # Required arguments
        parser.add_argument('output_dir', type=str, help='Directory to save exported files')
        
        # Optional arguments
        parser.add_argument('--format', type=str, choices=['json', 'csv'], 
                            default='json', help='Output format (default: json)')
        parser.add_argument('--customer-id', type=int, help='Filter by customer ID')
        parser.add_argument('--report-id', type=int, help='Export a specific report by ID')
        parser.add_argument('--start-date', type=str, help='Filter by start date (YYYY-MM-DD)')
        parser.add_argument('--end-date', type=str, help='Filter by end date (YYYY-MM-DD)')
        parser.add_argument('--combine', action='store_true', 
                            help='Combine all reports into a single file')
        parser.add_argument('--min-amount', type=float, help='Filter by minimum total amount')
        parser.add_argument('--max-amount', type=float, help='Filter by maximum total amount')

    def handle(self, *args, **options):
        output_dir = options['output_dir']
        export_format = options['format']
        customer_id = options.get('customer_id')
        report_id = options.get('report_id')
        start_date = options.get('start_date')
        end_date = options.get('end_date')
        combine = options.get('combine')
        min_amount = options.get('min_amount')
        max_amount = options.get('max_amount')
        
        # Create output directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        # Build query
        query = Q()
        if customer_id:
            query &= Q(customer_id=customer_id)
        if report_id:
            query &= Q(id=report_id)
        if start_date:
            query &= Q(start_date__gte=start_date)
        if end_date:
            query &= Q(end_date__lte=end_date)
        if min_amount:
            query &= Q(total_amount__gte=min_amount)
        if max_amount:
            query &= Q(total_amount__lte=max_amount)
            
        # Get reports
        reports = BillingReport.objects.filter(query)
        report_count = reports.count()
        
        if report_count == 0:
            self.stdout.write('No reports found matching criteria')
            return
            
        self.stdout.write(f'Found {report_count} reports to export')
        
        # Export reports
        if combine:
            # Combine all reports into a single file
            timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
            if export_format == 'json':
                # JSON format
                filename = f'billing_reports_combined_{timestamp}.json'
                file_path = os.path.join(output_dir, filename)
                
                # Convert all reports to dicts
                report_dicts = [report.to_dict() for report in reports]
                
                with open(file_path, 'w') as f:
                    json.dump(report_dicts, f, indent=2)
                    
                self.stdout.write(self.style.SUCCESS(f'Exported {report_count} reports to {file_path}'))
                
            else:
                # CSV format
                filename = f'billing_reports_combined_{timestamp}.csv'
                file_path = os.path.join(output_dir, filename)
                
                # Extract all service costs as flat records
                records = []
                for report in reports:
                    for order_cost in report.order_costs.all():
                        for service_cost in order_cost.service_costs.all():
                            records.append({
                                'report_id': report.id,
                                'customer_id': report.customer_id,
                                'customer_name': report.customer.company_name,
                                'start_date': report.start_date.strftime('%Y-%m-%d'),
                                'end_date': report.end_date.strftime('%Y-%m-%d'),
                                'order_id': order_cost.order.transaction_id,
                                'reference_number': order_cost.order.reference_number,
                                'service_id': service_cost.service_id,
                                'service_name': service_cost.service_name,
                                'amount': service_cost.amount
                            })
                
                # Write CSV file
                if records:
                    with open(file_path, 'w', newline='') as f:
                        writer = csv.DictWriter(f, fieldnames=records[0].keys())
                        writer.writeheader()
                        writer.writerows(records)
                        
                    self.stdout.write(self.style.SUCCESS(
                        f'Exported {len(records)} service cost records to {file_path}'
                    ))
                else:
                    self.stdout.write(self.style.WARNING('No service cost records found'))
                    
        else:
            # Export each report as a separate file
            exported_count = 0
            for report in reports:
                try:
                    # Generate filename
                    timestamp = report.created_at.strftime('%Y%m%d')
                    if export_format == 'json':
                        filename = f'billing_report_{report.id}_{timestamp}.json'
                        file_path = os.path.join(output_dir, filename)
                        
                        # Export as JSON
                        with open(file_path, 'w') as f:
                            json.dump(report.to_dict(), f, indent=2)
                            
                    else:
                        filename = f'billing_report_{report.id}_{timestamp}.csv'
                        file_path = os.path.join(output_dir, filename)
                        
                        # Export as CSV
                        with open(file_path, 'w', newline='') as f:
                            # Write header
                            f.write('order_id,service_id,service_name,amount\n')
                            
                            # Write rows
                            for order_cost in report.order_costs.all():
                                for service_cost in order_cost.service_costs.all():
                                    f.write(f'{order_cost.order.transaction_id},{service_cost.service_id},'
                                           f'"{service_cost.service_name}",{service_cost.amount}\n')
                    
                    exported_count += 1
                    
                except Exception as e:
                    self.stdout.write(self.style.ERROR(
                        f'Error exporting report {report.id}: {str(e)}'
                    ))
                    
            self.stdout.write(self.style.SUCCESS(f'Successfully exported {exported_count} reports'))