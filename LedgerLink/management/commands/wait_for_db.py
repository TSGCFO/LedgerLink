from django.core.management.base import BaseCommand
from django.db import connections
import time
import psycopg2
import os

class Command(BaseCommand):
    help = "Wait for database"
    
    def handle(self, *args, **kwargs):
        self.stdout.write("Waiting for database...")
        db_ready = False
        
        # Get database connection details from environment or use defaults
        db_host = os.environ.get('DB_HOST', 'db')
        db_name = os.environ.get('DB_NAME', 'ledgerlink_test')
        db_user = os.environ.get('DB_USER', 'postgres')
        db_password = os.environ.get('DB_PASSWORD', 'postgres')
        
        self.stdout.write(f"Connecting to {db_host}/{db_name} as {db_user}")
        
        max_attempts = 30
        attempts = 0
        
        while not db_ready and attempts < max_attempts:
            try:
                attempts += 1
                db_conn = psycopg2.connect(
                    host=db_host, 
                    user=db_user, 
                    password=db_password, 
                    dbname=db_name
                )
                db_conn.close()
                db_ready = True
                self.stdout.write(self.style.SUCCESS(f"Database ready after {attempts} attempts!"))
            except psycopg2.OperationalError as e:
                self.stdout.write(f"Database not ready (attempt {attempts}/{max_attempts}): {str(e)}")
                time.sleep(1)
        
        if not db_ready:
            self.stdout.write(self.style.ERROR(f"Database not available after {max_attempts} attempts"))
            return 1
            
        return 0