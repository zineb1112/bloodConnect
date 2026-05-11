import time
import psycopg2
from django.core.management.base import BaseCommand
import os

class Command(BaseCommand):
    help = 'Wait for database to be ready'

    def handle(self, *args, **options):
        self.stdout.write('Waiting for database...')
        max_retries = 30
        
        for i in range(max_retries):
            try:
                conn = psycopg2.connect(
                    dbname=os.environ.get('DB_NAME', 'blood_db'),
                    user=os.environ.get('DB_USER', 'blood_user'),
                    password=os.environ.get('DB_PASSWORD', 'blood_pass'),
                    host=os.environ.get('DB_HOST', 'db'),
                    port=os.environ.get('DB_PORT', '5432')
                )
                conn.close()
                self.stdout.write(self.style.SUCCESS('Database is ready!'))
                return
            except psycopg2.OperationalError:
                self.stdout.write(f'Attempt {i+1}/{max_retries}: Database not ready, waiting...')
                time.sleep(2)
        
        self.stdout.write(self.style.ERROR('Database did not become available in time!'))
        raise Exception('Database connection failed')