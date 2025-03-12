import json
import requests
from django.core.management.base import BaseCommand
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from rest_framework_simplejwt.tokens import RefreshToken
from customers.models import Customer


class Command(BaseCommand):
    help = 'Test the billing reports API'

    def handle(self, *args, **options):
        # 1. Get or create a superuser for testing
        User = get_user_model()
        user, created = User.objects.get_or_create(
            username='admin',
            email='admin@example.com',
            is_staff=True,
            is_superuser=True
        )
        if created:
            user.set_password('adminpass')
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Created superuser: {user.username}'))
        else:
            self.stdout.write(f'Using existing superuser: {user.username}')

        # 2. Get JWT token
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        self.stdout.write(f'Generated access token: {access_token[:10]}...')

        # 3. Test GET report list
        self.test_get_reports(access_token)

        # 4. Test generating a report
        self.test_generate_report(access_token)

    def test_get_reports(self, token):
        """Test GET /api/v2/reports/ endpoint"""
        url = 'http://localhost:8000/api/v2/reports/'
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }

        response = requests.get(url, headers=headers)
        self.stdout.write(f'GET {url} - Status: {response.status_code}')

        try:
            data = response.json()
            self.stdout.write(self.style.SUCCESS(f'Response: {json.dumps(data, indent=2)[:500]}...'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error parsing response: {str(e)}'))
            self.stdout.write(self.style.ERROR(f'Raw response: {response.text[:500]}...'))

    def test_generate_report(self, token):
        """Test POST /api/v2/reports/generate/ endpoint"""
        url = 'http://localhost:8000/api/v2/reports/generate/'
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }

        # Get first customer
        try:
            customer = Customer.objects.first()
            if not customer:
                self.stdout.write(self.style.ERROR('No customers found in database'))
                return
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error getting customer: {str(e)}'))
            return

        # Prepare report data
        data = {
            'customer_id': customer.id,
            'start_date': '2024-02-16',
            'end_date': '2024-03-10',
            'output_format': 'json'
        }

        self.stdout.write(f'Generating report for customer: {customer.company_name} (ID: {customer.id})')
        self.stdout.write(f'Using data: {json.dumps(data, indent=2)}')

        # Send POST request
        response = requests.post(url, headers=headers, json=data)
        self.stdout.write(f'POST {url} - Status: {response.status_code}')

        try:
            result = response.json()
            self.stdout.write(self.style.SUCCESS(f'Response: {json.dumps(result, indent=2)[:500]}...'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error parsing response: {str(e)}'))
            self.stdout.write(self.style.ERROR(f'Raw response: {response.text[:500]}...'))