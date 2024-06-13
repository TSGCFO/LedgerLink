# billing/management/commands/fix_sku_quantity.py
from django.core.management.base import BaseCommand
from billing.models import Order
import json

class Command(BaseCommand):
    help = 'Fix sku_quantity field in Order model to ensure it is a valid JSON string'

    def handle(self, *args, **kwargs):
        orders = Order.objects.all()
        for order in orders:
            if isinstance(order.sku_quantity, list):
                order.sku_quantity = json.dumps(order.sku_quantity)
                order.save()
        self.stdout.write(self.style.SUCCESS('Successfully fixed sku_quantity field in Order model'))
