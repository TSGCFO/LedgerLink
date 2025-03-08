from django.core.management.base import BaseCommand
from django.db import connections
import time
import psycopg2

class Command(BaseCommand):
    help = "Wait for database"
    
    def handle(self, *args, **kwargs):
        self.stdout.write("Waiting for database...")
        db_ready = False
        while not db_ready:
            try:
                db_conn = psycopg2.connect(
                    host="db", 
                    user="postgres", 
                    password="postgres", 
                    dbname="ledgerlink_test"
                )
                db_conn.close()
                db_ready = True
                self.stdout.write(self.style.SUCCESS("Database ready!"))
            except psycopg2.OperationalError:
                self.stdout.write("Database not ready, waiting 1 second...")
                time.sleep(1)