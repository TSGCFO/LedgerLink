# LedgerLink Testing Cheatsheet

This cheatsheet provides quick reference for common testing patterns in the LedgerLink application.

## Database Setup

### Test PostgreSQL Setup

```bash
# Create test database
createdb ledgerlink_test

# Run migrations on test database
DATABASE_URL=postgres://username:password@localhost/ledgerlink_test python manage.py migrate

# Run tests with specific database
DATABASE_URL=postgres://username:password@localhost/ledgerlink_test python -m pytest
```

### Testing Views and JSON Fields

```python
# Mock OrderSKUView for testing
from tests.integration.conftest import MockOrderSKUView

# Create mock view instance
view_mock = MockOrderSKUView(
    id=1,
    status='pending',
    order_date=timezone.now(),
    priority='normal',
    customer_id=1,
    sku_id='SKU001',
    quantity=10
)

# Test JSON field handling
sku_quantities = json.dumps({'SKU001': 10, 'SKU002': 5})
order = Order.objects.create(
    customer=customer,
    sku_quantities=sku_quantities
)
self.assertEqual(json.loads(order.sku_quantities).get('SKU001'), 10)
```

## Django Testing

### Model Tests

```python
# Test model validation
def test_order_validation(self):
    # Invalid order (missing required field)
    order = Order(status='pending')
    with self.assertRaises(ValidationError):
        order.full_clean()
    
    # Valid order
    order = Order(
        customer=self.customer,
        status='pending',
        sku_quantities=json.dumps({'SKU001': 5})
    )
    order.full_clean()  # Should not raise exception

# Test calculated property
def test_order_total_items(self):
    order = Order.objects.create(
        customer=self.customer,
        status='pending',
        sku_quantities=json.dumps({'SKU001': 5, 'SKU002': 10})
    )
    self.assertEqual(order.total_items, 15)

# Test model method
def test_mark_as_completed(self):
    order = Order.objects.create(
        customer=self.customer,
        status='pending',
        sku_quantities=json.dumps({'SKU001': 5})
    )
    order.mark_as_completed()
    self.assertEqual(order.status, 'completed')
```

### API Tests

```python
# Test API list endpoint
def test_order_list_api(self):
    url = reverse('order-list')
    response = self.client.get(url)
    self.assertEqual(response.status_code, 200)
    self.assertEqual(len(response.data), 2)

# Test API create endpoint
def test_order_create_api(self):
    url = reverse('order-list')
    data = {
        'customer': self.customer.id,
        'status': 'pending',
        'sku_quantities': {'SKU001': 5}
    }
    response = self.client.post(url, data, format='json')
    self.assertEqual(response.status_code, 201)
    self.assertEqual(Order.objects.count(), 3)

# Test API filter
def test_order_filter_api(self):
    url = reverse('order-list') + '?status=pending'
    response = self.client.get(url)
    self.assertEqual(response.status_code, 200)
    self.assertEqual(len(response.data), 1)
```

### Testing Complex Queries

```python
# Test query performance
def test_order_list_query_count(self):
    # Reset query count
    reset_queries()
    
    # Enable query counting
    with self.settings(DEBUG=True):
        # Make the request
        url = reverse('order-list')
        response = self.client.get(url)
        
        # Get query count
        query_count = len(connection.queries)
        
        # Check query count is reasonable
        self.assertLessEqual(query_count, 5)

# Test select_related/prefetch_related
def test_prefetch_related_query(self):
    # Reset query count
    reset_queries()
    
    with self.settings(DEBUG=True):
        # Get orders with prefetch_related
        list(Order.objects.all().prefetch_related('customer'))
        prefetch_query_count = len(connection.queries)
        
        # Get orders without prefetch_related
        reset_queries()
        for order in Order.objects.all():
            _ = order.customer.company_name
        regular_query_count = len(connection.queries)
        
        # Prefetch should use fewer queries
        self.assertLess(prefetch_query_count, regular_query_count)
```

## Testing Advanced Rules

### Testing Rule Conditions

```python
# Test simple rule condition
def test_basic_rule_condition(self):
    rule = Rule.objects.create(
        rule_group=self.rule_group,
        name='Test Rule',
        field='quantity',
        operator='gt',
        value='10',
        price_adjustment=5.0,
        adjustment_type='per_item'
    )
    
    # Test condition matches
    result = rule.evaluate({'quantity': 15})
    self.assertTrue(result)
    
    # Test condition doesn't match
    result = rule.evaluate({'quantity': 5})
    self.assertFalse(result)

# Test advanced rule with complex conditions
def test_advanced_rule_conditions(self):
    condition = {
        "operator": "and",
        "conditions": [
            {
                "field": "quantity",
                "operator": "gte",
                "value": 5
            },
            {
                "field": "sku_id",
                "operator": "in",
                "value": ["SKU001", "SKU002"]
            }
        ]
    }
    
    rule = AdvancedRule.objects.create(
        rule_group=self.rule_group,
        name='Complex Rule',
        conditions=json.dumps(condition),
        calculations=json.dumps({"type": "fixed", "value": 10.0})
    )
    
    # Helper function to evaluate complex conditions
    def evaluate_condition(condition, data):
        if "operator" in condition and condition["operator"] in ["and", "or"]:
            results = [evaluate_condition(sub_cond, data) for sub_cond in condition["conditions"]]
            return all(results) if condition["operator"] == "and" else any(results)
        else:
            field = condition["field"]
            operator = condition["operator"]
            value = condition["value"]
            
            if field not in data:
                return False
            
            field_value = data[field]
            
            if operator == "eq":
                return field_value == value
            elif operator == "gt":
                return field_value > value
            elif operator == "gte":
                return field_value >= value
            elif operator == "in":
                return field_value in value
            return False
    
    # Test data that matches
    result = evaluate_condition(json.loads(rule.conditions), {
        "quantity": 10,
        "sku_id": "SKU001"
    })
    self.assertTrue(result)
    
    # Test data that doesn't match
    result = evaluate_condition(json.loads(rule.conditions), {
        "quantity": 3,
        "sku_id": "SKU001"
    })
    self.assertFalse(result)
```

### Testing Tiered Pricing

```python
# Test case-based tier pricing
def test_tier_based_pricing(self):
    tier_config = {
        "tiers": [
            {"min": 0, "max": 10, "value": 1.00},
            {"min": 11, "max": 50, "value": 0.75},
            {"min": 51, "max": 999999, "value": 0.50}
        ]
    }
    
    rule = AdvancedRule.objects.create(
        rule_group=self.rule_group,
        name='Tier Rule',
        conditions=json.dumps({"field": "sku_id", "operator": "eq", "value": "SKU001"}),
        calculations=json.dumps({"type": "case_based_tier", "field": "quantity"}),
        tier_config=json.dumps(tier_config)
    )
    
    # Helper function to get tier value
    def get_tier_value(quantity, tier_config):
        for tier in tier_config["tiers"]:
            if tier["min"] <= quantity <= tier["max"]:
                return tier["value"]
        return None
    
    # Test different quantity values
    self.assertEqual(get_tier_value(5, tier_config), 1.00)
    self.assertEqual(get_tier_value(15, tier_config), 0.75)
    self.assertEqual(get_tier_value(100, tier_config), 0.50)
```

## Integration Testing

### Testing Cross-Module Integration

```python
# Test Order-Billing integration
def test_order_billing_integration(self):
    # Create order
    order = Order.objects.create(
        customer=self.customer,
        status='completed',
        sku_quantities=json.dumps({"SKU001": 10, "SKU002": 5})
    )
    
    # Create billing report for order
    report = BillingReport.objects.create(
        customer=self.customer,
        billing_date=timezone.now(),
        total_amount=150.00,
        created_by=self.user,
        details=json.dumps([
            {
                'sku': 'SKU001',
                'quantity': 10,
                'base_price': 10.00,
                'total': 100.00
            },
            {
                'sku': 'SKU002',
                'quantity': 5,
                'base_price': 10.00,
                'total': 50.00
            }
        ])
    )
    
    # Test order and billing report integration
    report_details = json.loads(report.details)
    order_quantities = json.loads(order.sku_quantities)
    
    # Verify quantities match
    for item in report_details:
        sku = item['sku']
        self.assertEqual(item['quantity'], order_quantities.get(sku, 0))
```

### Testing Rule-Based Pricing

```python
# Test rule application to order
def test_rule_application_to_order(self):
    # Create rule
    rule = Rule.objects.create(
        rule_group=self.rule_group,
        name='Quantity Rule',
        field='quantity',
        operator='gt',
        value='5',
        price_adjustment=2.50,
        adjustment_type='per_item'
    )
    
    # Create order
    order = Order.objects.create(
        customer=self.customer,
        status='pending',
        sku_quantities=json.dumps({"SKU001": 10})
    )
    
    # Create product
    product = Product.objects.create(
        name="Test Product",
        sku="SKU001",
        price=10.00
    )
    
    # Calculate price with rule
    base_price = product.price * 10  # 10 units
    rule_adjustment = 0
    
    # Apply rule if condition matches
    if 10 > int(rule.value):  # 10 > 5, so rule applies
        rule_adjustment = rule.price_adjustment * 10  # per_item adjustment
    
    total_price = base_price + rule_adjustment
    
    # Expected: 10 * $10 (base) + 10 * $2.50 (rule) = $125
    self.assertEqual(total_price, 125.00)
```

## Performance Testing

### Response Time Testing

```python
# Test endpoint response time
def test_api_response_time(self):
    url = reverse('order-list')
    
    # Measure response time
    start_time = time.time()
    response = self.client.get(url)
    end_time = time.time()
    
    # Calculate response time
    response_time = end_time - start_time
    
    # Verify response time is acceptable
    self.assertLess(response_time, 0.5)  # Less than 500ms
```

### Scaling Tests

```python
# Test scaling with data size
def test_scaling_performance(self):
    url = reverse('order-list')
    page_sizes = [10, 50, 100, 200]
    
    response_times = []
    for size in page_sizes:
        # Make request with different page size
        start_time = time.time()
        response = self.client.get(f"{url}?page_size={size}")
        end_time = time.time()
        
        response_time = end_time - start_time
        response_times.append(response_time)
    
    # Verify response time scales reasonably (sublinearly)
    if len(response_times) > 1:
        scaling_ratio = response_times[-1] / response_times[0]
        data_ratio = page_sizes[-1] / page_sizes[0]
        
        self.assertLess(scaling_ratio, data_ratio)
```

## Contract Testing

### Defining Pact Contracts

```python
# Define contract for order API
def create_order_contract():
    pact.given('orders exist').upon_receiving('a request for all orders').with_request(
        method='GET',
        path='/api/orders/',
        headers={'Authorization': 'Bearer valid-token'}
    ).will_respond_with(
        status=200,
        headers={'Content-Type': 'application/json'},
        body=[
            {
                'id': 1,
                'customer': 1,
                'status': 'pending',
                'sku_quantities': {'SKU001': 5, 'SKU002': 10}
            },
            {
                'id': 2,
                'customer': 2,
                'status': 'completed',
                'sku_quantities': {'SKU003': 3, 'SKU004': 7}
            }
        ]
    )
```

### Verify Provider Implementation

```python
# Set up provider state
@staticmethod
def setup_provider_state(state_name, state_params=None):
    """Set up test data based on provider state"""
    if state_name == 'orders exist':
        # Create test orders
        order1, _ = Order.objects.get_or_create(
            id=1,
            defaults={
                'customer': customer1,
                'status': 'pending',
                'sku_quantities': json.dumps({'SKU001': 5, 'SKU002': 10})
            }
        )
        
        order2, _ = Order.objects.get_or_create(
            id=2,
            defaults={
                'customer': customer2,
                'status': 'completed',
                'sku_quantities': json.dumps({'SKU003': 3, 'SKU004': 7})
            }
        )
    
    return {'result': True, 'providerState': state_name}
```

## Common Testing Patterns

### Testing JSON Fields

```python
# Create object with JSON field
order = Order.objects.create(
    customer=self.customer,
    status='pending',
    sku_quantities=json.dumps({'SKU001': 5, 'SKU002': 10})
)

# Read and modify JSON field
sku_quantities = json.loads(order.sku_quantities)
sku_quantities['SKU001'] = 7
order.sku_quantities = json.dumps(sku_quantities)
order.save()

# Verify updated value
updated_order = Order.objects.get(id=order.id)
updated_quantities = json.loads(updated_order.sku_quantities)
self.assertEqual(updated_quantities['SKU001'], 7)
```

### Testing Database Views

```python
# Test database view through Django ORM
def test_orderskuview_query(self):
    # Create order with multiple SKUs
    order = Order.objects.create(
        customer=self.customer,
        status='pending',
        sku_quantities=json.dumps({'SKU001': 5, 'SKU002': 10})
    )
    
    # Create products
    Product.objects.create(sku='SKU001', name='Product 1', price=10.00)
    Product.objects.create(sku='SKU002', name='Product 2', price=15.00)
    
    # Query the view through a custom manager or raw query
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT * FROM orders_orderskuview
            WHERE id = %s
        """, [order.id])
        rows = cursor.fetchall()
    
    # Verify view results
    self.assertEqual(len(rows), 2)  # Two SKUs in the order
```

### Testing Authentication Requirements

```python
# Test authenticated endpoint
def test_authenticated_endpoint(self):
    url = reverse('order-list')
    
    # Unauthenticated request should fail
    self.client.logout()
    response = self.client.get(url)
    self.assertEqual(response.status_code, 401)
    
    # Authenticated request should succeed
    self.client.force_login(self.user)
    response = self.client.get(url)
    self.assertEqual(response.status_code, 200)
```

### Testing Permissions

```python
# Test permission-based access
def test_permissions(self):
    # Create users with different permissions
    admin_user = User.objects.create_user('admin', password='admin123')
    admin_user.is_staff = True
    admin_user.save()
    
    regular_user = User.objects.create_user('regular', password='user123')
    
    # Create object owned by admin
    order = Order.objects.create(
        customer=self.customer,
        status='pending',
        created_by=admin_user
    )
    
    # Test admin can access
    self.client.force_login(admin_user)
    url = reverse('order-detail', args=[order.id])
    response = self.client.get(url)
    self.assertEqual(response.status_code, 200)
    
    # Test regular user cannot access
    self.client.force_login(regular_user)
    response = self.client.get(url)
    self.assertEqual(response.status_code, 403)
```

## Test Case Organization

### Fixtures & Common Setup

```python
# Create base test class with common setup
class BaseTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        """Set up data for all tests in class - runs once"""
        cls.user = User.objects.create_user(
            username='testuser',
            password='password123'
        )
        
        cls.customer = Customer.objects.create(
            company_name="Test Company",
            contact_name="Test Contact",
            email="test@example.com",
            is_active=True
        )
    
    def setUp(self):
        """Runs before each test method"""
        self.client = Client()
        self.client.force_login(self.user)

# Inherit from base test case
class OrderTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        # Add order-specific setup
        self.order = Order.objects.create(
            customer=self.customer,
            status='pending',
            sku_quantities=json.dumps({'SKU001': 5})
        )
```

### Using TestCase vs TransactionTestCase

```python
# Use TestCase for most tests (faster)
class StandardTests(TestCase):
    def test_something(self):
        # Tests run inside a transaction that is rolled back
        pass

# Use TransactionTestCase when testing transactions
from django.test import TransactionTestCase

class TransactionTests(TransactionTestCase):
    def test_database_transactions(self):
        # Changes persist between tests and are not rolled back
        # Good for testing transaction behavior
        pass
```

## Running Tests

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test billing

# Run specific test class
python manage.py test billing.tests.BillingCalculatorTests

# Run specific test method
python manage.py test billing.tests.BillingCalculatorTests.test_tier_pricing

# Run with pytest
python -m pytest

# Run pytest with coverage
python -m pytest --cov=.

# Run tests in parallel
python -m pytest -xvs -n 4
```