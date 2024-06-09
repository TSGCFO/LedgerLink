from django.core.management.base import BaseCommand
from billing.models import Material

class Command(BaseCommand):
    help = 'Load initial material data'

    def handle(self, *args, **kwargs):
        material_data = [
            {'name': 'BUBBLE WRAP', 'unit_price': 0.02},
            {'name': 'FRAGILE STICKER', 'unit_price': 0.15},
            {'name': 'PALLETS', 'unit_price': 9.50},
            {'name': 'SHRINK WRAP', 'unit_price': 4.00},
            {'name': 'PACKING POUCH', 'unit_price': 0.07},
            {'name': 'INVOICE', 'unit_price': 0.13},
            {'name': 'MAILER', 'unit_price': 0.49},
            {'name': 'INSULATED MAILER', 'unit_price': 3.12},
            {'name': 'SHIPPING LABEL', 'unit_price': 0.05},
            {'name': 'SMALL LABEL', 'unit_price': 0.25},
            {'name': 'Miso US Soup Label', 'unit_price': 0.10},
            {'name': 'Edge Protectors', 'unit_price': 0.93},
        ]

        for material in material_data:
            Material.objects.create(
                name=material['name'],
                unit_price=material['unit_price']
            )

        self.stdout.write(self.style.SUCCESS('Successfully loaded initial material data'))
