#!/usr/bin/env python
"""
Import customer services data from a CSV file.
"""
import csv
import os
import sys
import django
from datetime import datetime

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'LedgerLink.settings')
django.setup()

from customer_services.models import CustomerService
from customers.models import Customer
from services.models import Service

def parse_datetime(dt_str):
    """Parse datetime string from CSV."""
    # Handle timezone format like '2024-12-10 23:27:13.509364-05'
    if dt_str.count('-') > 2:  # Has timezone in format -05
        parts = dt_str.rsplit('-', 1)
        if len(parts) == 2 and parts[1].isdigit():
            # Convert '-05' to '-0500' format which datetime can parse
            dt_str = parts[0] + '-' + parts[1].zfill(2) + '00'
    
    try:
        # Try standard format with timezone
        return datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S.%f%z')
    except ValueError:
        try:
            # Try without timezone
            return datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S.%f')
        except ValueError:
            try:
                # Try without microseconds but with timezone
                return datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S%z')
            except ValueError:
                # Try without microseconds and timezone
                return datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')

def import_customer_services(csv_path):
    """Import customer services from CSV file."""
    count = 0
    errors = 0
    skipped = 0
    
    with open(csv_path, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        
        for row in reader:
            try:
                customer_id = int(row['customer_id'])
                service_id = int(row['service_id'])
                
                # Check if customer and service exist
                try:
                    customer = Customer.objects.get(id=customer_id)
                    service = Service.objects.get(id=service_id)
                except (Customer.DoesNotExist, Service.DoesNotExist) as e:
                    print(f"Error: {e} - Row: {row}")
                    errors += 1
                    continue
                
                # Check if relation already exists
                if CustomerService.objects.filter(customer=customer, service=service).exists():
                    print(f"Skipping existing customer service: {customer.id} - {service.id}")
                    skipped += 1
                    continue
                
                # Create customer service
                cs = CustomerService(
                    id=int(row['id']),
                    unit_price=float(row['unit_price']),
                    created_at=parse_datetime(row['created_at']),
                    updated_at=parse_datetime(row['updated_at']),
                    customer=customer,
                    service=service
                )
                cs.save()
                count += 1
                
            except Exception as e:
                print(f"Error importing row: {row}")
                print(f"Error details: {e}")
                errors += 1
    
    return count, errors, skipped

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <csv_file>")
        sys.exit(1)
    
    csv_path = sys.argv[1]
    imported, errors, skipped = import_customer_services(csv_path)
    
    print(f"Import complete:")
    print(f"  Imported: {imported}")
    print(f"  Skipped: {skipped}")
    print(f"  Errors: {errors}")