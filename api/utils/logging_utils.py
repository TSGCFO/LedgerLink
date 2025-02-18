"""
Logging utilities for backend components
"""

import logging
import functools
import time
import traceback
from typing import Any, Callable, Dict, Optional, Type

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