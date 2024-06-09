import csv
from django.core.management.base import BaseCommand
from billing.models import Service

class Command(BaseCommand):
    help = 'Load initial services data into the Service model'

    def handle(self, *args, **kwargs):
        services = [
            {"service_name": "B2B-CASE PICK"},
            {"service_name": "B2B-PALLET PICK"},
            {"service_name": "B2B-MATCHA TEA"},
            {"service_name": "B2C-CASE PICK"},
            {"service_name": "B2C-PALLET PICK"},
            {"service_name": "B2C-MATCHA TEA"},
            {"service_name": "RUSH ORDER"},
            {"service_name": "PALLET PAPERWORK"},
            {"service_name": "KITTING"},
            {"service_name": "RE LABELLING"},
            {"service_name": "QC"},
            {"service_name": "R-BOX"},
            {"service_name": "R-PALLET"},
            {"service_name": "R-SKU"},
            {"service_name": "R-rush receiving"},
            {"service_name": "RETURNS"},
            {"service_name": "CROSS DOCK"},
            {"service_name": "WALMART"},
        ]

        for service in services:
            Service.objects.create(**service)

        self.stdout.write(self.style.SUCCESS('Successfully loaded service data'))
