from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal, InvalidOperation
import logging
import json

logger = logging.getLogger('billing')

class ReportDataValidator:
    """Validator for report data structure and content"""
    
    @staticmethod
    def validate_report_data(data):
        """Validate the report data structure and content"""
        if not isinstance(data, dict):
            raise ValidationError("Report data must be a dictionary")

        required_fields = ['orders', 'total_amount']
        for field in required_fields:
            if field not in data:
                raise ValidationError(f"Missing required field: {field}")

        if not isinstance(data['orders'], list):
            raise ValidationError("Orders must be a list")

        # Validate orders
        for order in data['orders']:
            if not isinstance(order, dict):
                raise ValidationError("Each order must be a dictionary")

            required_order_fields = ['order_id', 'services', 'total_amount']
            for field in required_order_fields:
                if field not in order:
                    raise ValidationError(f"Order missing required field: {field}")

            if not isinstance(order['services'], list):
                raise ValidationError("Order services must be a list")

            # Validate services
            for service in order['services']:
                if not isinstance(service, dict):
                    raise ValidationError("Each service must be a dictionary")

                required_service_fields = ['service_id', 'service_name', 'amount']
                for field in required_service_fields:
                    if field not in service:
                        raise ValidationError(f"Service missing required field: {field}")

        # Validate total amount
        try:
            total_amount = Decimal(str(data['total_amount']))
            if total_amount < 0:
                raise ValidationError("Total amount cannot be negative")

            # Validate that order amounts sum up to total
            order_sum = sum(Decimal(str(order['total_amount'])) for order in data['orders'])
            if total_amount != order_sum:
                raise ValidationError("Order amounts do not sum up to total amount")

        except (ValueError, TypeError, InvalidOperation):
            raise ValidationError("Invalid amount format")

class ReportFileHandler:
    """Handler for report file operations"""

    @staticmethod
    def estimate_file_size(data):
        """Estimate the size of the generated report file"""
        try:
            # Rough estimation based on JSON string length
            json_size = len(json.dumps(data))
            # Excel/PDF typically larger than JSON
            estimated_size = json_size * 1.5
            return estimated_size
        except Exception as e:
            logger.error(f"Error estimating file size: {str(e)}")
            return float('inf')

    @staticmethod
    def validate_file_size(size):
        """Validate if the estimated file size is within limits"""
        max_size = getattr(settings, 'MAX_REPORT_SIZE', 10 * 1024 * 1024)  # Default 10MB
        if size > max_size:
            raise ValidationError(f"Estimated file size ({size} bytes) exceeds maximum allowed size ({max_size} bytes)")

    @staticmethod
    def get_file_extension(format):
        """Get the appropriate file extension for the given format"""
        format_extensions = {
            'excel': 'xlsx',
            'pdf': 'pdf',
            'csv': 'csv'
        }
        return format_extensions.get(format, '')

    @staticmethod
    def get_content_type(format):
        """Get the appropriate content type for the given format"""
        content_types = {
            'excel': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'pdf': 'application/pdf',
            'csv': 'text/csv'
        }
        return content_types.get(format, 'application/octet-stream')

class ReportCache:
    """Handler for report caching operations"""

    @staticmethod
    def get_cache_key(customer_id, start_date, end_date, format='preview'):
        """Generate a cache key for the report"""
        return f'billing_report_{customer_id}_{start_date}_{end_date}_{format}'

    @staticmethod
    def get_cached_report(customer_id, start_date, end_date, format='preview'):
        """Retrieve a cached report if available"""
        from django.core.cache import cache
        cache_key = ReportCache.get_cache_key(customer_id, start_date, end_date, format)
        return cache.get(cache_key)

    @staticmethod
    def cache_report(customer_id, start_date, end_date, data, format='preview'):
        """Cache a report for future use"""
        from django.core.cache import cache
        cache_key = ReportCache.get_cache_key(customer_id, start_date, end_date, format)
        timeout = getattr(settings, 'REPORT_CACHE_TIMEOUT', 3600)  # Default 1 hour
        cache.set(cache_key, data, timeout=timeout)

class ReportFormatter:
    """Handler for report formatting operations"""

    @staticmethod
    def format_currency(amount):
        """Format amount as currency"""
        try:
            return f"${Decimal(str(amount)):.2f}"
        except (ValueError, TypeError, InvalidOperation):
            return "$0.00"

    @staticmethod
    def format_date(date):
        """Format date consistently"""
        try:
            return date.strftime(settings.DATE_FORMAT)
        except AttributeError:
            return str(date)

    @staticmethod
    def format_service_description(service):
        """Format service description consistently"""
        return f"{service['service_name']}: {ReportFormatter.format_currency(service['amount'])}"

def log_report_generation(func):
    """Decorator to log report generation details"""
    def wrapper(*args, **kwargs):
        start_time = timezone.now()
        logger.info(f"Starting report generation with args: {args}, kwargs: {kwargs}")
        
        try:
            result = func(*args, **kwargs)
            duration = (timezone.now() - start_time).total_seconds()
            logger.info(f"Report generation completed in {duration:.2f} seconds")
            return result
        except Exception as e:
            duration = (timezone.now() - start_time).total_seconds()
            logger.error(f"Report generation failed after {duration:.2f} seconds: {str(e)}")
            raise
    
    return wrapper 