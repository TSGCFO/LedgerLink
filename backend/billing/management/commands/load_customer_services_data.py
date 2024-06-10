from django.core.management.base import BaseCommand
from billing.models import CustomerService, Service, Customer

class Command(BaseCommand):
    help = 'Load initial customer services data into the CustomerService model'

    def handle(self, *args, **kwargs):
        customer_id = 4
        customer = Customer.objects.get(pk=customer_id)

        customer_services = [
            {"service_name": "B2C PICK", "unit_price": 0.25},
            {"service_name": "B2C-CASE PICK", "unit_price": 0.53},
            {"service_name": "RUSH", "unit_price": 12.5},
            {"service_name": "B2C-MATCHA TEA", "unit_price": 0.26},
            {"service_name": "B2C FLATBOX", "unit_price": 0.85},
            {"service_name": "B2C Base", "unit_price": 2.5},
            {"service_name": "B2B Base", "unit_price": 6.25},
            {"service_name": "B2B FLATBOX", "unit_price": 0.85},
            {"service_name": "PALLET PAPERWORK", "unit_price": 2.75},
            {"service_name": "RUSH ORDER", "unit_price": 12.5},
            {"service_name": "B2B-PALLET PICK", "unit_price": 2.5},
            {"service_name": "B2B-CASE PICK", "unit_price": 0.53},
            {"service_name": "B2C-MATCHA PICK", "unit_price": 0.26},
            {"service_name": "Costco-Unit Pick", "unit_price": 0.22},
            {"service_name": "Costco-Double Packing", "unit_price": 0.52},
        ]

        for cs in customer_services:
            service, created = Service.objects.get_or_create(service_name=cs["service_name"])
            CustomerService.objects.create(customer=customer, service=service, unit_price=cs["unit_price"])

        self.stdout.write(self.style.SUCCESS('Successfully loaded customer services data'))
