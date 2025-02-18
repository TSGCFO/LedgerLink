from django.utils import timezone
from django.conf import settings
from rest_framework.views import exception_handler
from datetime import datetime
import re
import json
import uuid

def generate_unique_id(prefix=''):
    """
    Generate a unique identifier with an optional prefix.
    Example: generate_unique_id('ORD') -> 'ORD-2024-ABC123'
    """
    timestamp = timezone.now().strftime('%Y%m%d')
    unique = str(uuid.uuid4()).split('-')[0].upper()
    return f"{prefix}-{timestamp}-{unique}"

def format_currency(amount, currency='USD'):
    """
    Format a decimal number as currency.
    Example: format_currency(1234.5) -> '$1,234.50'
    """
    try:
        amount = float(amount)
        if currency == 'USD':
            return f"${amount:,.2f}"
        return f"{amount:,.2f} {currency}"
    except (ValueError, TypeError):
        return None

def validate_email(email):
    """
    Validate email format using regex.
    Returns True if valid, False otherwise.
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_phone(phone):
    """
    Validate phone number format.
    Supports multiple formats including international numbers.
    """
    # Remove all non-numeric characters
    phone = re.sub(r'\D', '', phone)
    # Check if the remaining number is valid
    return 10 <= len(phone) <= 15

def format_phone(phone):
    """
    Format phone number consistently.
    Example: format_phone('1234567890') -> '(123) 456-7890'
    """
    # Remove all non-numeric characters
    phone = re.sub(r'\D', '', phone)
    
    if len(phone) == 10:
        return f"({phone[:3]}) {phone[3:6]}-{phone[6:]}"
    elif len(phone) == 11 and phone.startswith('1'):
        return f"+1 ({phone[1:4]}) {phone[4:7]}-{phone[7:]}"
    return phone

def parse_date(date_str):
    """
    Parse date string in multiple formats.
    Returns datetime object or None if invalid.
    """
    formats = [
        '%Y-%m-%d',
        '%m/%d/%Y',
        '%d-%m-%Y',
        '%Y/%m/%d',
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    return None

def format_date(date_obj, format_str=None):
    """
    Format date object using specified format or default format.
    """
    if not date_obj:
        return None
    
    if format_str:
        return date_obj.strftime(format_str)
    
    return date_obj.strftime(settings.DATE_FORMAT)

def clean_dict(data):
    """
    Remove None values from dictionary recursively.
    """
    if not isinstance(data, dict):
        return data
    
    return {
        key: clean_dict(value)
        for key, value in data.items()
        if value is not None
    }

def merge_dicts(dict1, dict2):
    """
    Deep merge two dictionaries.
    """
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dicts(result[key], value)
        else:
            result[key] = value
    
    return result

def serialize_decimal(obj):
    """
    JSON serializer for decimal objects.
    """
    if hasattr(obj, 'decimal'):
        return str(obj)
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

def safe_json_dumps(data):
    """
    Safely serialize data to JSON, handling decimal types.
    """
    return json.dumps(data, default=serialize_decimal)

def get_client_ip(request):
    """
    Get client IP address from request.
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')

def mask_sensitive_data(data, fields=None):
    """
    Mask sensitive data in dictionary.
    """
    if fields is None:
        fields = ['password', 'credit_card', 'ssn', 'secret']
    
    if isinstance(data, dict):
        return {
            key: mask_sensitive_data(value, fields) if key not in fields
            else '****' for key, value in data.items()
        }
    return data

class Singleton:
    """
    Singleton metaclass for ensuring only one instance of a class.
    """
    _instances = {}
    
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

def retry_operation(times=3, exceptions=(Exception,), delay=0):
    """
    Decorator for retrying operations that may fail.
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            for i in range(times):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if i == times - 1:
                        raise
                    if delay:
                        import time
                        time.sleep(delay)
            return None
        return wrapper
    return decorator

def paginate_queryset(queryset, page_size, page_number):
    """
    Manual pagination helper for querysets.
    """
    try:
        page_size = int(page_size)
        page_number = int(page_number)
    except (TypeError, ValueError):
        page_size = 10
        page_number = 1
    
    start = (page_number - 1) * page_size
    end = start + page_size
    
    total_count = queryset.count()
    total_pages = (total_count + page_size - 1) // page_size
    
    return {
        'items': queryset[start:end],
        'total_count': total_count,
        'total_pages': total_pages,
        'current_page': page_number,
        'page_size': page_size,
        'has_next': page_number < total_pages,
        'has_previous': page_number > 1
    }

def get_model_fields(model):
    """
    Get all field names from a Django model.
    """
    return [field.name for field in model._meta.get_fields()]

def format_filesize(size):
    """
    Format file size in bytes to human readable format.
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} PB"