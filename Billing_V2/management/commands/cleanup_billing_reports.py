import logging
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from django.db.models import Q
from ...models import BillingReport

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Cleanup old billing reports'

    def add_arguments(self, parser):
        parser.add_argument('--days', type=int, default=90, 
                            help='Delete reports older than this many days (default: 90)')
        parser.add_argument('--customer-id', type=int, 
                            help='Limit cleanup to a specific customer')
        parser.add_argument('--dry-run', action='store_true', 
                            help='Show what would be deleted without actually deleting')

    def handle(self, *args, **options):
        days = options.get('days')
        customer_id = options.get('customer_id')
        dry_run = options.get('dry_run')
        
        # Calculate cutoff date
        cutoff_date = timezone.now() - timedelta(days=days)
        self.stdout.write(f'Cleaning up billing reports older than {cutoff_date.strftime("%Y-%m-%d")}')
        
        # Build query
        query = Q(created_at__lt=cutoff_date)
        if customer_id:
            query &= Q(customer_id=customer_id)
            self.stdout.write(f'Limiting to customer ID: {customer_id}')
            
        # Get reports to delete
        reports = BillingReport.objects.filter(query)
        report_count = reports.count()
        
        if report_count == 0:
            self.stdout.write('No reports found matching criteria')
            return
            
        self.stdout.write(f'Found {report_count} reports to delete')
        
        # Preview reports if dry run
        if dry_run:
            self.stdout.write('DRY RUN - no reports will be deleted')
            for report in reports:
                self.stdout.write(f'Would delete: Report {report.id} for {report.customer.company_name} '
                                 f'created on {report.created_at.strftime("%Y-%m-%d")}')
            return
            
        # Confirm deletion
        if not options.get('no_input', False):
            confirm = input(f'Are you sure you want to delete {report_count} reports? [y/N] ')
            if confirm.lower() != 'y':
                self.stdout.write('Aborted')
                return
        
        # Delete reports
        try:
            with transaction.atomic():
                # Get order costs to cascade delete
                order_cost_count = sum(report.order_costs.count() for report in reports)
                
                # Delete reports
                deleted, _ = reports.delete()
                
                self.stdout.write(self.style.SUCCESS(
                    f'Successfully deleted {deleted} reports with {order_cost_count} order costs'
                ))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error deleting reports: {str(e)}'))