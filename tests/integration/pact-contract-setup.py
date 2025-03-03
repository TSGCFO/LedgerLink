import json
import os
from pact import Consumer, Provider

# Configure Pact
PACT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pacts')
os.makedirs(PACT_DIR, exist_ok=True)

# Create a Consumer-driven contract
consumer = Consumer('LedgerLinkFrontend')
provider = Provider('LedgerLinkBackend')
pact = consumer.has_pact_with(provider, pact_dir=PACT_DIR)

# Example Consumer contract for Order API
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
                'order_date': '2025-03-01T10:00:00Z',
                'sku_quantities': {'SKU001': 5, 'SKU002': 10}
            },
            {
                'id': 2,
                'customer': 2,
                'status': 'completed',
                'order_date': '2025-02-28T10:00:00Z',
                'sku_quantities': {'SKU003': 3, 'SKU004': 7}
            }
        ]
    )
    
    pact.given('an order with ID 1 exists').upon_receiving('a request for a specific order').with_request(
        method='GET',
        path='/api/orders/1/',
        headers={'Authorization': 'Bearer valid-token'}
    ).will_respond_with(
        status=200,
        headers={'Content-Type': 'application/json'},
        body={
            'id': 1,
            'customer': 1,
            'status': 'pending',
            'order_date': '2025-03-01T10:00:00Z',
            'sku_quantities': {'SKU001': 5, 'SKU002': 10}
        }
    )
    
    pact.given('order can be created').upon_receiving('a request to create an order').with_request(
        method='POST',
        path='/api/orders/',
        headers={
            'Content-Type': 'application/json',
            'Authorization': 'Bearer valid-token'
        },
        body={
            'customer': 1,
            'sku_quantities': {'SKU001': 5, 'SKU002': 10}
        }
    ).will_respond_with(
        status=201,
        headers={'Content-Type': 'application/json'},
        body={
            'id': 3,
            'customer': 1,
            'status': 'pending',
            'order_date': '2025-03-02T10:00:00Z',
            'sku_quantities': {'SKU001': 5, 'SKU002': 10}
        }
    )

# Example Consumer contract for Rules API
def create_rules_contract():
    pact.given('rules exist').upon_receiving('a request for all rules').with_request(
        method='GET',
        path='/api/rules/advanced-rules/',
        headers={'Authorization': 'Bearer valid-token'}
    ).will_respond_with(
        status=200,
        headers={'Content-Type': 'application/json'},
        body=[
            {
                'id': 1,
                'rule_group': 1,
                'name': 'Volume Discount',
                'description': 'Applies discount for large orders',
                'conditions': json.dumps({'field': 'quantity', 'operator': 'gt', 'value': 10}),
                'calculations': json.dumps({'type': 'percent_discount', 'value': 5.0}),
                'tier_config': None
            },
            {
                'id': 2,
                'rule_group': 1,
                'name': 'Tiered Pricing',
                'description': 'Applies tiered pricing based on quantity',
                'conditions': json.dumps({'field': 'sku_id', 'operator': 'in', 'value': ['SKU001', 'SKU002']}),
                'calculations': json.dumps({'type': 'case_based_tier', 'field': 'quantity'}),
                'tier_config': json.dumps({
                    'tiers': [
                        {'min': 0, 'max': 10, 'value': 1.00},
                        {'min': 11, 'max': 50, 'value': 0.75},
                        {'min': 51, 'max': 1000, 'value': 0.50}
                    ]
                })
            }
        ]
    )
    
    pact.given('a rule with ID 1 exists').upon_receiving('a request for a specific rule').with_request(
        method='GET',
        path='/api/rules/advanced-rules/1/',
        headers={'Authorization': 'Bearer valid-token'}
    ).will_respond_with(
        status=200,
        headers={'Content-Type': 'application/json'},
        body={
            'id': 1,
            'rule_group': 1,
            'name': 'Volume Discount',
            'description': 'Applies discount for large orders',
            'conditions': json.dumps({'field': 'quantity', 'operator': 'gt', 'value': 10}),
            'calculations': json.dumps({'type': 'percent_discount', 'value': 5.0}),
            'tier_config': None
        }
    )

# Example Consumer contract for Billing API
def create_billing_contract():
    pact.given('billing reports exist').upon_receiving('a request for all billing reports').with_request(
        method='GET',
        path='/api/billing/reports/',
        headers={'Authorization': 'Bearer valid-token'}
    ).will_respond_with(
        status=200,
        headers={'Content-Type': 'application/json'},
        body=[
            {
                'id': 1,
                'customer': 1,
                'billing_date': '2025-03-01T00:00:00Z',
                'total_amount': '150.00',
                'details': json.dumps([
                    {
                        'sku': 'SKU001',
                        'quantity': 5,
                        'base_price': 10.00,
                        'total': 50.00
                    },
                    {
                        'sku': 'SKU002',
                        'quantity': 10,
                        'base_price': 10.00,
                        'total': 100.00
                    }
                ])
            },
            {
                'id': 2,
                'customer': 2,
                'billing_date': '2025-02-28T00:00:00Z',
                'total_amount': '220.00',
                'details': json.dumps([
                    {
                        'sku': 'SKU003',
                        'quantity': 3,
                        'base_price': 20.00,
                        'total': 60.00
                    },
                    {
                        'sku': 'SKU004',
                        'quantity': 8,
                        'base_price': 20.00,
                        'total': 160.00
                    }
                ])
            }
        ]
    )
    
    pact.given('billing can be calculated').upon_receiving('a request to calculate billing').with_request(
        method='POST',
        path='/api/billing/calculate/',
        headers={
            'Content-Type': 'application/json',
            'Authorization': 'Bearer valid-token'
        },
        body={
            'customer_id': 1,
            'order_ids': [1, 2],
            'date_range': {
                'start_date': '2025-03-01',
                'end_date': '2025-03-31'
            }
        }
    ).will_respond_with(
        status=200,
        headers={'Content-Type': 'application/json'},
        body={
            'customer_id': 1,
            'total_amount': '370.00',
            'line_items': [
                {
                    'order_id': 1,
                    'sku': 'SKU001',
                    'quantity': 5,
                    'base_price': 10.00,
                    'adjustments': [],
                    'total': 50.00
                },
                {
                    'order_id': 1,
                    'sku': 'SKU002',
                    'quantity': 10,
                    'base_price': 10.00,
                    'adjustments': [],
                    'total': 100.00
                },
                {
                    'order_id': 2,
                    'sku': 'SKU003',
                    'quantity': 3,
                    'base_price': 20.00,
                    'adjustments': [],
                    'total': 60.00
                },
                {
                    'order_id': 2,
                    'sku': 'SKU004',
                    'quantity': 8,
                    'base_price': 20.00,
                    'adjustments': [],
                    'total': 160.00
                }
            ]
        }
    )

# Generate contracts
if __name__ == '__main__':
    # Setup contracts
    create_order_contract()
    create_rules_contract()
    create_billing_contract()
    
    # Write Pact files to disk
    pact.honour_pact()
    
    print(f"Pact contracts have been written to: {PACT_DIR}")