# rules/billing_engine.py

from typing import List, Dict, Any
from orders.models import Order
from services.models import Service
from customer_services.models import CustomerService


class BillingEngine:
    def __init__(self, customer_id: int):
        self.customer_id = customer_id

    def fetch_orders(self) -> List[Order]:
        return Order.objects.filter(customer_id=self.customer_id)

    def get_service_ids(self, service_names: List[str]) -> Dict[str, int]:
        services = Service.objects.filter(service_name__in=service_names)
        return {service.service_name: service.id for service in services}

    def get_customer_services(self, service_ids: List[int]) -> List[CustomerService]:
        return CustomerService.objects.filter(
            service_id__in=service_ids,
            customer_id=self.customer_id
        )

    def apply_criteria(self, order: Order, criteria: List[Dict[str, Any]], prices: Dict[int, float],
                       service_ids: Dict[str, int]) -> Dict[str, float]:
        costs = {}
        for criterion in criteria:
            service_name = criterion['service_name']
            apply_logic = criterion['apply_logic']
            service_id = service_ids.get(service_name, 0)
            price = prices.get(service_id, 0)
            if apply_logic == 'always':
                costs[service_name] = price
            elif apply_logic == 'custom_logic_1':
                costs[service_name] = self.calculate_custom_logic_1(order, service_id, price, criterion['parameters'])
            elif apply_logic == 'custom_logic_2':
                costs[service_name] = self.calculate_custom_logic_2(order, service_id, price, criterion['parameters'])
            # Add more conditions as needed
        return costs

    def calculate_custom_logic_1(self, order: Order, service_id: int, price: float, params: Dict[str, Any]) -> float:
        # Implement custom logic 1
        pass

    def calculate_custom_logic_2(self, order: Order, service_id: int, price: float, params: Dict[str, Any]) -> float:
        # Implement custom logic 2
        pass

    def generate_report_data(self, orders: List[Order], criteria: List[Dict[str, Any]], service_ids: Dict[str, int],
                             prices: Dict[int, float]) -> List[Dict[str, Any]]:
        report_data = []
        for order in orders:
            costs = self.apply_criteria(order, criteria, prices, service_ids)
            report_data.append({
                'transaction_id': order.transaction_id,
                'customer_id': order.customer_id,
                'costs': costs,
                # Include other fields as needed
            })
        return report_data
