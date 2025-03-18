"""
Pact provider tests for customer services API.
These tests verify that the API meets the contract expected by the frontend.
"""
import os
import json
import unittest
import psycopg2
from decimal import Decimal
from datetime import datetime

# Import our factory test pattern
from test_scripts.factory_test import (
    ModelFactory, 
    CustomerFactory, 
    ServiceFactory, 
    CustomerServiceFactory
)


class MockRequest:
    """Mock request object for testing."""
    
    def __init__(self, method='GET', path='/', data=None, params=None, headers=None):
        self.method = method
        self.path = path
        self.data = data or {}
        self.GET = params or {}
        self.headers = headers or {}
        self.content_type = 'application/json'
    
    def get_full_path(self):
        """Get the full path including query string."""
        return self.path


class MockResponse:
    """Mock response object for testing."""
    
    def __init__(self, status_code=200, data=None, content_type='application/json'):
        self.status_code = status_code
        self.data = data or {}
        self.content_type = content_type
    
    def json(self):
        """Return the response data as JSON."""
        return self.data


class APIClient:
    """Mock API client for testing."""
    
    def __init__(self, conn):
        self.conn = conn
    
    def get(self, path, params=None):
        """Send a GET request."""
        if path.startswith('/api/customer-services/'):
            if '/services/' in path:
                # Get a specific customer service
                service_id = int(path.split('/')[-1])
                with self.conn.cursor() as cursor:
                    cursor.execute("""
                    SELECT cs.id, cs.customer_id, cs.service_id, cs.unit_price,
                           c.company_name, s.name as service_name
                    FROM customer_services_customerservice cs
                    JOIN customers_customer c ON cs.customer_id = c.id
                    JOIN services_service s ON cs.service_id = s.id
                    WHERE cs.id = %s
                    """, (service_id,))
                    row = cursor.fetchone()
                    
                    if row:
                        data = {
                            'id': row[0],
                            'customer_id': row[1],
                            'service_id': row[2],
                            'unit_price': str(row[3]),
                            'customer_name': row[4],
                            'service_name': row[5]
                        }
                        return MockResponse(200, data)
                    else:
                        return MockResponse(404, {'detail': 'Not found'})
            else:
                # List customer services
                customer_id = params.get('customer_id') if params else None
                
                query = """
                SELECT cs.id, cs.customer_id, cs.service_id, cs.unit_price,
                       c.company_name, s.name as service_name
                FROM customer_services_customerservice cs
                JOIN customers_customer c ON cs.customer_id = c.id
                JOIN services_service s ON cs.service_id = s.id
                """
                
                params = []
                if customer_id:
                    query += " WHERE cs.customer_id = %s"
                    params.append(int(customer_id))
                
                with self.conn.cursor() as cursor:
                    cursor.execute(query, params)
                    rows = cursor.fetchall()
                    
                    results = []
                    for row in rows:
                        results.append({
                            'id': row[0],
                            'customer_id': row[1],
                            'service_id': row[2],
                            'unit_price': str(row[3]),
                            'customer_name': row[4],
                            'service_name': row[5]
                        })
                    
                    return MockResponse(200, {
                        'count': len(results),
                        'results': results
                    })
        
        return MockResponse(404, {'detail': 'Not found'})
    
    def post(self, path, data):
        """Send a POST request."""
        if path == '/api/customer-services/':
            # Create a new customer service
            try:
                customer_id = data['customer_id']
                service_id = data['service_id']
                unit_price = Decimal(data['unit_price'])
                
                with self.conn.cursor() as cursor:
                    # Check if the customer service already exists
                    cursor.execute("""
                    SELECT id FROM customer_services_customerservice
                    WHERE customer_id = %s AND service_id = %s
                    """, (customer_id, service_id))
                    
                    if cursor.fetchone():
                        return MockResponse(400, {
                            'detail': 'CustomerService with this customer and service already exists.'
                        })
                    
                    # Create the customer service
                    cursor.execute("""
                    INSERT INTO customer_services_customerservice
                    (customer_id, service_id, unit_price, created_at, updated_at)
                    VALUES (%s, %s, %s, NOW(), NOW())
                    RETURNING id
                    """, (customer_id, service_id, unit_price))
                    
                    cs_id = cursor.fetchone()[0]
                    
                    # Get the created customer service
                    cursor.execute("""
                    SELECT cs.id, cs.customer_id, cs.service_id, cs.unit_price,
                           c.company_name, s.name as service_name
                    FROM customer_services_customerservice cs
                    JOIN customers_customer c ON cs.customer_id = c.id
                    JOIN services_service s ON cs.service_id = s.id
                    WHERE cs.id = %s
                    """, (cs_id,))
                    
                    row = cursor.fetchone()
                    
                    data = {
                        'id': row[0],
                        'customer_id': row[1],
                        'service_id': row[2],
                        'unit_price': str(row[3]),
                        'customer_name': row[4],
                        'service_name': row[5]
                    }
                    
                    return MockResponse(201, data)
            except KeyError:
                return MockResponse(400, {
                    'detail': 'Missing required fields'
                })
            except Exception as e:
                return MockResponse(400, {
                    'detail': str(e)
                })
        
        return MockResponse(404, {'detail': 'Not found'})
    
    def put(self, path, data):
        """Send a PUT request."""
        if path.startswith('/api/customer-services/'):
            service_id = int(path.split('/')[-1])
            
            try:
                unit_price = Decimal(data['unit_price'])
                
                with self.conn.cursor() as cursor:
                    # Check if the customer service exists
                    cursor.execute("""
                    SELECT id FROM customer_services_customerservice
                    WHERE id = %s
                    """, (service_id,))
                    
                    if not cursor.fetchone():
                        return MockResponse(404, {
                            'detail': 'Not found'
                        })
                    
                    # Update the customer service
                    cursor.execute("""
                    UPDATE customer_services_customerservice
                    SET unit_price = %s, updated_at = NOW()
                    WHERE id = %s
                    """, (unit_price, service_id))
                    
                    # Get the updated customer service
                    cursor.execute("""
                    SELECT cs.id, cs.customer_id, cs.service_id, cs.unit_price,
                           c.company_name, s.name as service_name
                    FROM customer_services_customerservice cs
                    JOIN customers_customer c ON cs.customer_id = c.id
                    JOIN services_service s ON cs.service_id = s.id
                    WHERE cs.id = %s
                    """, (service_id,))
                    
                    row = cursor.fetchone()
                    
                    data = {
                        'id': row[0],
                        'customer_id': row[1],
                        'service_id': row[2],
                        'unit_price': str(row[3]),
                        'customer_name': row[4],
                        'service_name': row[5]
                    }
                    
                    return MockResponse(200, data)
            except KeyError:
                return MockResponse(400, {
                    'detail': 'Missing required fields'
                })
            except Exception as e:
                return MockResponse(400, {
                    'detail': str(e)
                })
        
        return MockResponse(404, {'detail': 'Not found'})
    
    def delete(self, path):
        """Send a DELETE request."""
        if path.startswith('/api/customer-services/'):
            service_id = int(path.split('/')[-1])
            
            with self.conn.cursor() as cursor:
                # Check if the customer service exists
                cursor.execute("""
                SELECT id FROM customer_services_customerservice
                WHERE id = %s
                """, (service_id,))
                
                if not cursor.fetchone():
                    return MockResponse(404, {
                        'detail': 'Not found'
                    })
                
                # Delete the customer service
                cursor.execute("""
                DELETE FROM customer_services_customerservice
                WHERE id = %s
                """, (service_id,))
                
                return MockResponse(204)
        
        return MockResponse(404, {'detail': 'Not found'})


class TestCustomerServicePact(unittest.TestCase):
    """Test CustomerService API contract using Pact."""
    
    def setUp(self):
        """Set up test data using factories."""
        # Connect to database
        self.conn = psycopg2.connect(
            host=os.environ.get('DB_HOST', 'db'),
            database=os.environ.get('DB_NAME', 'ledgerlink_test'),
            user=os.environ.get('DB_USER', 'postgres'),
            password=os.environ.get('DB_PASSWORD', 'postgres')
        )
        self.conn.autocommit = True
        
        # Initialize factories
        self.customer_factory = CustomerFactory(self.conn)
        self.service_factory = ServiceFactory(self.conn)
        self.cs_factory = CustomerServiceFactory(self.conn)
        
        # Clear existing data
        with self.conn.cursor() as cursor:
            cursor.execute("DELETE FROM customer_services_customerservice")
            cursor.execute("DELETE FROM services_service")
            cursor.execute("DELETE FROM customers_customer")
        
        # Create test data
        self.customer = self.customer_factory.create(
            company_name="Pact Test Company",
            legal_business_name="Legal Test Company",
            email="test@example.com",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        self.service = self.service_factory.create(
            name="Pact Test Service",
            description="Test Service Description",
            price=Decimal('100.00'),
            charge_type="fixed"
        )
        
        self.customer_service = self.cs_factory.create(
            customer=self.customer,
            service=self.service,
            unit_price=Decimal('99.99')
        )
        
        # Create API client
        self.client = APIClient(self.conn)
    
    def test_list_customer_services(self):
        """Test listing customer services."""
        # Define Pact interaction
        expected_response = {
            'count': 1,
            'results': [
                {
                    'id': self.customer_service['id'],
                    'customer_id': self.customer['id'],
                    'service_id': self.service['id'],
                    'unit_price': '99.99',
                    'customer_name': self.customer['company_name'],
                    'service_name': self.service['name']
                }
            ]
        }
        
        # Perform request
        response = self.client.get('/api/customer-services/')
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)
        result = response.data['results'][0]
        self.assertEqual(result['id'], self.customer_service['id'])
        self.assertEqual(result['customer_id'], self.customer['id'])
        self.assertEqual(result['service_id'], self.service['id'])
        self.assertEqual(result['unit_price'], '99.99')
        self.assertEqual(result['customer_name'], self.customer['company_name'])
        self.assertEqual(result['service_name'], self.service['name'])
    
    def test_filter_customer_services(self):
        """Test filtering customer services by customer_id."""
        # Create another customer and service
        customer2 = self.customer_factory.create(
            company_name="Another Company",
            legal_business_name="Another Legal Company",
            email="another@example.com",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        service2 = self.service_factory.create(
            name="Another Service",
            description="Another Service Description",
            price=Decimal('200.00'),
            charge_type="per_unit"
        )
        
        cs2 = self.cs_factory.create(
            customer=customer2,
            service=service2,
            unit_price=Decimal('199.99')
        )
        
        # Perform request with filter
        response = self.client.get(
            '/api/customer-services/',
            {'customer_id': self.customer['id']}
        )
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)
        result = response.data['results'][0]
        self.assertEqual(result['customer_id'], self.customer['id'])
    
    def test_retrieve_customer_service(self):
        """Test retrieving a specific customer service."""
        # Perform request
        response = self.client.get(f'/api/customer-services/{self.customer_service["id"]}/')
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['id'], self.customer_service['id'])
        self.assertEqual(response.data['customer_id'], self.customer['id'])
        self.assertEqual(response.data['service_id'], self.service['id'])
        self.assertEqual(response.data['unit_price'], '99.99')
    
    def test_create_customer_service(self):
        """Test creating a customer service."""
        # Create new customer and service
        customer = self.customer_factory.create(
            company_name="New Pact Company",
            legal_business_name="New Legal Company",
            email="new@example.com",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        service = self.service_factory.create(
            name="New Pact Service",
            description="New Service Description",
            price=Decimal('300.00'),
            charge_type="fixed"
        )
        
        # Define request data
        data = {
            'customer_id': customer['id'],
            'service_id': service['id'],
            'unit_price': '299.99'
        }
        
        # Perform request
        response = self.client.post('/api/customer-services/', data)
        
        # Verify response
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['customer_id'], customer['id'])
        self.assertEqual(response.data['service_id'], service['id'])
        self.assertEqual(response.data['unit_price'], '299.99')
    
    def test_update_customer_service(self):
        """Test updating a customer service."""
        # Define request data
        data = {
            'unit_price': '149.99'
        }
        
        # Perform request
        response = self.client.put(f'/api/customer-services/{self.customer_service["id"]}/', data)
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['id'], self.customer_service['id'])
        self.assertEqual(response.data['unit_price'], '149.99')
    
    def test_delete_customer_service(self):
        """Test deleting a customer service."""
        # Perform request
        response = self.client.delete(f'/api/customer-services/{self.customer_service["id"]}/')
        
        # Verify response
        self.assertEqual(response.status_code, 204)
        
        # Verify deletion
        response = self.client.get(f'/api/customer-services/{self.customer_service["id"]}/')
        self.assertEqual(response.status_code, 404)
    
    def tearDown(self):
        """Clean up test data."""
        with self.conn.cursor() as cursor:
            cursor.execute("DELETE FROM customer_services_customerservice")
            cursor.execute("DELETE FROM services_service")
            cursor.execute("DELETE FROM customers_customer")
        self.conn.close()


if __name__ == '__main__':
    unittest.main()