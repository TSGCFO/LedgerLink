from django.core.management.base import BaseCommand
from django.db import connection
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Refreshes all materialized views in the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--concurrent',
            action='store_true',
            help='Refresh views concurrently (only works if views are already populated)',
        )

    def handle(self, *args, **options):
        concurrent = options.get('concurrent', False)
        concurrently = "CONCURRENTLY" if concurrent else ""
        
        views = [
            'orders_sku_view',
            'customer_services_customerserviceview'
        ]
        
        for view in views:
            try:
                start_time = timezone.now()
                self.stdout.write(f"Starting refresh of {view} at {start_time}")
                
                with connection.cursor() as cursor:
                    cursor.execute(f'REFRESH MATERIALIZED VIEW {concurrently} {view}')
                
                end_time = timezone.now()
                duration = (end_time - start_time).total_seconds()
                
                success_message = f'Successfully refreshed {view} in {duration:.2f} seconds'
                self.stdout.write(self.style.SUCCESS(success_message))
                logger.info(success_message)
                
            except Exception as e:
                error_message = f'Error refreshing {view}: {str(e)}'
                self.stdout.write(self.style.ERROR(error_message))
                logger.error(error_message)
