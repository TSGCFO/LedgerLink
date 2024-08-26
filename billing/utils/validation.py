# billing/utils/validation.py

def validate_positive_amount(value):
    """Ensure that the amount is positive."""
    if value < 0:
        raise ValueError("Amount must be positive.")
    return value

def validate_currency_format(value):
    """Ensure the value is in a correct currency format."""
    try:
        value = float(value)
        if value < 0:
            raise ValueError("Currency value cannot be negative.")
    except ValueError:
        raise ValueError("Invalid currency format.")
    return value

def validate_order_integrity(order):
    """Validate that an order has all necessary data before processing."""
    if not order.reference_number:
        raise ValueError("Order must have a reference number.")
    if order.total_item_qty is None or order.total_item_qty <= 0:
        raise ValueError("Order must have a positive total item quantity.")
    return True
