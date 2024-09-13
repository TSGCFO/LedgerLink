from django.db.models import Q
from orders.models import Order
from datetime import datetime

def fetch_orders(customer, start_date, end_date):
    """
    Fetch orders for a given customer within a specific date range.
    
    :param customer: Customer object
    :param start_date: datetime object representing the start of the date range
    :param end_date: datetime object representing the end of the date range
    :return: QuerySet of Order objects
    """
    return Order.objects.filter(
        Q(customer=customer) &
        Q(close_date__range=(start_date, end_date))
    ).order_by('close_date')

def get_order_details(order):
    """
    Extract relevant details from an order for billing purposes.
    
    :param order: Order object
    :return: dict containing order details
    """
    return {
        'transaction_id': order.transaction_id,
        'reference_number': order.reference_number,
        'close_date': order.close_date,
        'ship_to_name': order.ship_to_name,
        'ship_to_company': order.ship_to_company,
        'ship_to_address': order.ship_to_address,
        'ship_to_city': order.ship_to_city,
        'ship_to_state': order.ship_to_state,
        'ship_to_zip': order.ship_to_zip,
        'ship_to_country': order.ship_to_country,
        'weight_lb': order.weight_lb,
        'line_items': order.line_items,
        'sku_quantity': order.sku_quantity,
        'total_item_qty': order.total_item_qty,
        'volume_cuft': order.volume_cuft,
        'packages': order.packages,
        'notes': order.notes,
        'carrier': order.carrier,
    }