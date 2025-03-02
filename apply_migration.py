#!/usr/bin/env python
"""
Script to apply the migration to fix missing tables and views.
"""
import os
import sys
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'LedgerLink.settings')
django.setup()

from django.core.management import call_command

def apply_migration():
    """Apply the migration to fix missing tables and views."""
    print("Applying migration to fix missing tables and views...")
    call_command('migrate', 'customer_services', '0006_create_missing_tables_and_views')
    print("Migration applied successfully!")

if __name__ == '__main__':
    apply_migration()