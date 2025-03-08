# Billing App

The billing app is responsible for generating billing reports based on customer orders and services.

## Key Components

- **BillingReport**: Model for storing generated billing reports
- **BillingReportDetail**: Model for order-specific costs within a report
- **BillingCalculator**: Service for calculating billing amounts based on rules
- **RuleEvaluator**: Utility for evaluating rules against orders
- **Exporters**: Services for exporting billing reports to various formats

## Testing

The billing app has a comprehensive test suite organized by test type.

### Test Directory Structure

```
billing/
  tests/
    test_models/      - Model tests
    test_views/       - API endpoint tests
    test_serializers/ - Serializer tests
    test_calculator/  - Calculator logic tests
    test_integration/ - Integration tests
    test_rules/       - Rule evaluator tests
    test_tiers/       - Case-based tier tests
    test_exporters/   - Exporter tests
    test_services/    - Service tests
    test_utils/       - Utility function tests
```

### Running Tests

To run all billing tests:

```bash
./run_billing_tests_reorganized.sh
```

For more details, see [billing/tests/README.md](tests/README.md).

## Implementation Notes

- The billing calculator uses the rules system to determine applicable services
- Rule evaluation supports various operators including equality, comparison, and containment
- Case-based tiers allow for quantity-based pricing with min/max thresholds
- All billing calculations are stored with full audit history