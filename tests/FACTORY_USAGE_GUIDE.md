# Test Factory Usage Guide

This guide explains how to use the test factories defined in `tests/factories.py` to create realistic test data for your tests.

## Overview

The LedgerLink project includes a comprehensive set of test factories that generate realistic test data based on production patterns. These factories are built using the `factory_boy` library and are designed to make writing tests easier and more consistent.

## Getting Started

To use the factories in your tests, import them from the `tests.factories` module:

```python
from tests.factories import (
    CustomerFactory, 
    OrderFactory,
    ProductFactory,
    # Import other factories as needed
)
```

## Basic Factory Usage

The simplest way to use a factory is to call it directly:

```python
# Create a customer
customer = CustomerFactory()

# Create an order for this customer
order = OrderFactory(customer=customer)

# Create a product for this customer
product = ProductFactory(customer=customer)
```

All factories handle creating related objects automatically, but you can override this by passing specific related objects.

## Key Factory Classes

### Customer Factories

- `CustomerFactory`: Basic customer with default values
- `RetailCustomerFactory`: Customer with business_type='Retail'
- `ManufacturingCustomerFactory`: Customer with business_type='Manufacturing'
- `DistributionCustomerFactory`: Customer with business_type='Distribution'
- `RealisticCustomerFactory`: Customer with realistic company name patterns

```python
# Create a realistic customer
customer = RealisticCustomerFactory()
```

### Order Factories

- `OrderFactory`: Basic order with numeric transaction_id
- Status-specific factories:
  - `SubmittedOrderFactory`: Order with status='submitted'
  - `ShippedOrderFactory`: Order with status='shipped'
  - `DeliveredOrderFactory`: Order with status='delivered'
  - `CancelledOrderFactory`: Order with status='cancelled'
- Priority-specific factories:
  - `HighPriorityOrderFactory`: Order with priority='high'
  - `LowPriorityOrderFactory`: Order with priority='low'
- Special-purpose factories:
  - `LargeOrderFactory`: Order with many SKUs (for performance testing)
  - `OrderWithComplexDataFactory`: Order with nested SKU data structure
  - `RealisticOrderFactory`: Order with realistic SKU patterns

```python
# Create an order with shipped status
shipped_order = ShippedOrderFactory(customer=customer)

# Create a high priority order
priority_order = HighPriorityOrderFactory(customer=customer)
```

### Service Factories

- `ServiceFactory`: Basic service with random charge_type
- Charge-type specific factories:
  - `FixedChargeServiceFactory`: Service with charge_type='fixed'
  - `PerUnitServiceFactory`: Service with charge_type='per_unit'
  - `TieredServiceFactory`: Service with charge_type='tiered'
  - `CaseTierServiceFactory`: Service with charge_type='case_based_tier'

```python
# Create a tiered service
tiered_service = TieredServiceFactory()

# Link a customer to this service
customer_service = CustomerServiceFactory(
    customer=customer,
    service=tiered_service
)
```

### Rule Factories

- `RuleGroupFactory`: Creates rule groups
- `RuleFactory`: Creates basic rules
- `AdvancedRuleFactory`: Creates advanced rules with complex conditions and calculations

```python
# Create a rule group for a customer service
rule_group = RuleGroupFactory(customer_service=customer_service)

# Add a rule to this group
rule = RuleFactory(rule_group=rule_group)

# Add an advanced rule with complex conditions
advanced_rule = AdvancedRuleFactory(rule_group=rule_group)
```

### Billing Factories

- `BillingReportFactory`: Creates billing reports with realistic data
- `BillingReportDetailFactory`: Creates billing report details

```python
# Create a billing report for a customer
billing_report = BillingReportFactory(customer=customer)

# Add details for an order
billing_detail = BillingReportDetailFactory(
    report=billing_report,
    order=order
)
```

### Other Factories

- `ProductFactory`: Creates products
- `MaterialFactory`: Creates materials with properties
- `BoxPriceFactory`: Creates box prices with dimensions
- `USShippingFactory` and `CADShippingFactory`: Create shipping records
- `InsertFactory`: Creates inserts

```python
# Create a material
material = MaterialFactory()

# Create a box price for this material
box_price = BoxPriceFactory(material=material)

# Create shipping for an order
shipping = USShippingFactory(order=order)

# Create an insert
insert = InsertFactory(material=material)
```

## Factory Traits

You can add traits to factories to add specific behaviors:

```python
# Create an order with detailed notes
order_with_notes = OrderFactory.create(WithNotesTrait())

# Create an order with tracking history
order_with_history = OrderFactory.create(WithTrackingHistoryTrait())
```

## Helper Functions

The factories module includes helper functions for creating complex test scenarios:

- `create_order_with_services(customer=None, service_count=None)`: Creates an order with associated services
- `create_billing_scenario(orders_count=None)`: Creates a complete billing scenario with customer, orders, services, and billing report

```python
# Create an order with 3 services
order, services, rules = create_order_with_services(
    customer=customer,
    service_count=3
)

# Create a complete billing scenario with 5 orders
customer, orders, report, details = create_billing_scenario(orders_count=5)
```

## Best Practices

1. **Use Explicit Dependencies**: When a test depends on specific relationships between objects, specify them explicitly rather than relying on factory defaults.

2. **Use Specialized Factories**: Use the most specific factory for your test case. For example, use `ShippedOrderFactory` instead of manually setting the status on an `OrderFactory`.

3. **Minimize Database Usage**: For unit tests, consider using `build()` instead of `create()` to avoid database operations:

   ```python
   # Builds object without saving to database
   customer = CustomerFactory.build()
   ```

4. **Consistent Test Data**: Use factories consistently across your test suite to ensure all tests use the same data patterns.

5. **Realistic Data Patterns**: Use the realistic factories for integration or system tests to ensure your tests work with data patterns that match production.

6. **Batch Creation**: For performance tests that need many objects, use batch creation:

   ```python
   # Create 50 customers
   customers = CustomerFactory.create_batch(50)
   ```

7. **Factory Inheritance**: Extend existing factories when you need slight variations.

## Example Test Cases

See `tests/test_factories_sample.py` for comprehensive examples of how to use these factories in test cases.

## Debugging Factory Issues

If you encounter issues with factories:

1. **Inspect Created Objects**: Print the attributes of created objects to see what data was generated
2. **Check Database Constraints**: Ensure your factories create data that meets database constraints
3. **Review Factory Definitions**: Check for circular dependencies or missing fields
4. **Database Transactions**: Ensure tests use transactions to roll back factory-created data
5. **Test in Isolation**: Test each factory in isolation to identify which one is causing problems

## Contributing New Factories

When adding new factories:

1. Add them to `tests/factories.py`
2. Follow the existing patterns and naming conventions
3. Use real-world data patterns when known
4. Add specialized variants for common use cases
5. Add example usage to `tests/test_factories_sample.py`

## Need Help?

If you need help using these factories or need new factory types, contact the development team.