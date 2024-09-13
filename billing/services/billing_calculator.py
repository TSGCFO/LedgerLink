from ..utils.order_fetcher import fetch_orders, get_order_details
from ..utils.rule_applier import apply_rules
from customer_services.models import CustomerService
from decimal import Decimal


def calculate_service_cost(customer_service, order, adjustment_amount):
    # Basic calculation: unit price * quantity + adjustment
    # This may need to be adjusted based on your specific pricing logic
    base_price = customer_service.unit_price * order.total_item_qty
    return base_price + Decimal(str(adjustment_amount))


class BillingCalculator:
    def __init__(self, customer, start_date, end_date):
        self.customer = customer
        self.start_date = start_date
        self.end_date = end_date

    def calculate_billing(self):
        orders = fetch_orders(self.customer, self.start_date, self.end_date)
        total_bill = Decimal('0.00')
        billing_details = []

        for order in orders:
            order_details = get_order_details(order)
            applicable_services = apply_rules(order, self.customer)
            order_total = Decimal('0.00')
            order_services = []

            for customer_service, adjustment_amount in applicable_services:
                service_cost = calculate_service_cost(customer_service, order, adjustment_amount)
                order_total += service_cost
                order_services.append({
                    'service_name': customer_service.service.service_name,
                    'cost': service_cost
                })

            billing_details.append({
                'order': order_details,
                'services': order_services,
                'total': order_total
            })
            total_bill += order_total

        return {
            'customer': self.customer.company_name,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'total_bill': total_bill,
            'billing_details': billing_details
        }

    def generate_invoice_data(self):
        billing_result = self.calculate_billing()

        invoice_data = {
            'customer_name': billing_result['customer'],
            'billing_period': f"{billing_result['start_date']} to {billing_result['end_date']}",
            'total_amount': billing_result['total_bill'],
            'line_items': []
        }

        for detail in billing_result['billing_details']:
            for service in detail['services']:
                invoice_data['line_items'].append({
                    'description': f"{service['service_name']} for Order {detail['order']['transaction_id']}",
                    'quantity': detail['order']['total_item_qty'],
                    'unit_price': service['cost'] / detail['order']['total_item_qty'],
                    'total': service['cost']
                })

        return invoice_data