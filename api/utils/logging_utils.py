"""
Logging utilities for backend components and client-side log handling
"""

import logging
import functools
import time
import traceback
import os
import json
import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Type, Union

# Get loggers for different components
api_logger = logging.getLogger('api')
rules_logger = logging.getLogger('rules')
orders_logger = logging.getLogger('orders')
customers_logger = logging.getLogger('customers')
products_logger = logging.getLogger('products')
billing_logger = logging.getLogger('billing')
shipping_logger = logging.getLogger('shipping')

def log_view_access(logger: Optional[logging.Logger] = None) -> Callable:
    """
    Decorator to log view access with timing and error tracking
    
    Usage:
        @log_view_access(logger=customers_logger)
        def my_view(request, *args, **kwargs):
            ...
    """
    def decorator(view_func: Callable) -> Callable:
        @functools.wraps(view_func)
        def wrapper(request, *args, **kwargs):
            start_time = time.time()
            view_logger = logger or api_logger
            
            # Log request
            view_logger.info(
                f"View access: {view_func.__name__}",
                extra={
                    'view': view_func.__name__,
                    'method': request.method,
                    'path': request.path,
                    'user': str(request.user) if request.user.is_authenticated else 'anonymous',
                    'args': args,
                    'kwargs': kwargs
                }
            )
            
            try:
                # Execute view
                response = view_func(request, *args, **kwargs)
                duration = time.time() - start_time
                
                # Log success
                view_logger.info(
                    f"View success: {view_func.__name__}",
                    extra={
                        'view': view_func.__name__,
                        'duration': f"{duration:.3f}s",
                        'status_code': getattr(response, 'status_code', None)
                    }
                )
                return response
                
            except Exception as e:
                duration = time.time() - start_time
                
                # Log error
                view_logger.error(
                    f"View error: {view_func.__name__}",
                    extra={
                        'view': view_func.__name__,
                        'duration': f"{duration:.3f}s",
                        'error': str(e),
                        'traceback': traceback.format_exc()
                    }
                )
                raise
                
        return wrapper
    return decorator

def log_model_access(logger: Optional[logging.Logger] = None) -> Callable:
    """
    Decorator to log model operations
    
    Usage:
        @log_model_access(logger=orders_logger)
        def create_order(self, *args, **kwargs):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            model_logger = logger or api_logger
            
            # Get model name from first arg (self)
            model_name = args[0].__class__.__name__ if args else 'Unknown'
            
            # Log operation start
            model_logger.info(
                f"Model operation: {func.__name__} on {model_name}",
                extra={
                    'model': model_name,
                    'operation': func.__name__,
                    'args': args[1:],  # Exclude self
                    'kwargs': kwargs
                }
            )
            
            try:
                # Execute operation
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                # Log success
                model_logger.info(
                    f"Model operation success: {func.__name__} on {model_name}",
                    extra={
                        'model': model_name,
                        'operation': func.__name__,
                        'duration': f"{duration:.3f}s",
                        'result': str(result) if result else None
                    }
                )
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                
                # Log error
                model_logger.error(
                    f"Model operation error: {func.__name__} on {model_name}",
                    extra={
                        'model': model_name,
                        'operation': func.__name__,
                        'duration': f"{duration:.3f}s",
                        'error': str(e),
                        'traceback': traceback.format_exc()
                    }
                )
                raise
                
        return wrapper
    return decorator

def log_error(error: Exception, context: Dict[str, Any] = None, logger: Optional[logging.Logger] = None) -> None:
    """
    Utility function to log errors with context
    
    Usage:
        try:
            ...
        except Exception as e:
            log_error(e, {'order_id': order.id}, orders_logger)
    """
    error_logger = logger or api_logger
    
    error_data = {
        'error_type': type(error).__name__,
        'error_message': str(error),
        'traceback': traceback.format_exc()
    }
    
    if context:
        error_data['context'] = context
        
    error_logger.error(
        f"Error occurred: {type(error).__name__}",
        extra=error_data
    )

def get_component_logger(component_name: str) -> logging.Logger:
    """
    Get logger for a specific component
    
    Usage:
        logger = get_component_logger('orders')
    """
    return logging.getLogger(component_name)


# Client-Side Log Handling

# Directory to store client-side logs
CLIENT_LOGS_DIR = Path('logs/client')

def ensure_logs_directory():
    """Ensure the logs directory exists"""
    os.makedirs(CLIENT_LOGS_DIR, exist_ok=True)

def save_client_logs(logs: List[Dict], user_info: Optional[Dict] = None) -> Dict:
    """
    Save client logs to a file in the logs directory
    
    Args:
        logs: List of log entries from the client
        user_info: Information about the user (email, id, etc.)
    
    Returns:
        Dict: Status and filename of the saved log file
    """
    ensure_logs_directory()
    
    # Create a timestamp for the filename
    timestamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
    
    # Create a unique filename
    user_id = user_info.get('id', 'anonymous') if user_info else 'anonymous'
    filename = f"client-logs-{user_id}-{timestamp}.json"
    filepath = CLIENT_LOGS_DIR / filename
    
    # Add metadata to the logs
    metadata = {
        "timestamp": datetime.datetime.now().isoformat(),
        "user": user_info,
        "log_count": len(logs)
    }
    
    # Save the logs with metadata
    try:
        with open(filepath, 'w') as f:
            json.dump({
                "metadata": metadata,
                "logs": logs
            }, f, indent=2)
        
        api_logger.info(f"Saved {len(logs)} client logs to {filename}")
        return {
            "success": True,
            "filename": filename,
            "log_count": len(logs)
        }
    except Exception as e:
        api_logger.error(f"Error saving client logs: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

def list_client_log_files() -> List[Dict]:
    """
    List all client log files
    
    Returns:
        List[Dict]: List of log filenames with metadata
    """
    ensure_logs_directory()
    
    try:
        files = []
        for filepath in CLIENT_LOGS_DIR.glob('*.json'):
            try:
                stat = filepath.stat()
                files.append({
                    "filename": filepath.name,
                    "size": stat.st_size,
                    "created": datetime.datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    "path": str(filepath)
                })
            except Exception as e:
                api_logger.error(f"Error reading file {filepath}: {str(e)}")
        
        return sorted(files, key=lambda x: x["created"], reverse=True)
    except Exception as e:
        api_logger.error(f"Error listing log files: {str(e)}")
        return []

def get_client_log_file_content(filename: str) -> Dict:
    """
    Read the content of a client log file
    
    Args:
        filename: Name of the log file
    
    Returns:
        Dict: Content of the log file
    """
    filepath = CLIENT_LOGS_DIR / filename
    
    if not filepath.exists():
        return {
            "success": False,
            "error": "File not found"
        }
    
    try:
        with open(filepath, 'r') as f:
            content = json.load(f)
        
        return {
            "success": True,
            "content": content
        }
    except Exception as e:
        api_logger.error(f"Error reading log file {filename}: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }