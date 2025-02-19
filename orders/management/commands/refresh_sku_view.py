from django.core.management.base import BaseCommand
from django.db import connection
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Refreshes the orders_sku_view materialized view'

    def handle(self, *args, **options):
        try:
            start_time = timezone.now()
            self.stdout.write(f"Starting view refresh at {start_time}")
            
            with connection.cursor() as cursor:
                cursor.execute('REFRESH MATERIALIZED VIEW CONCURRENTLY orders_sku_view')
            
            end_time = timezone.now()
            duration = (end_time - start_time).total_seconds()
            
            success_message = f'Successfully refreshed orders_sku_view in {duration:.2f} seconds'
            self.stdout.write(self.style.SUCCESS(success_message))
            logger.info(success_message)
            
        except Exception as e:
            error_message = f'Error refreshing orders_sku_view: {str(e)}'
            self.stdout.write(self.style.ERROR(error_message))
            logger.error(error_message)
            raise 