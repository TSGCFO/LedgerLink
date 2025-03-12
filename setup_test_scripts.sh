#!/bin/bash
set -e

# Make all test scripts executable
echo "Making all test scripts executable..."

chmod +x run_docker_tests.sh
chmod +x run_materials_tests.sh
chmod +x run_api_tests.sh
chmod +x run_billing_tests.sh
chmod +x run_bulk_operations_tests.sh
chmod +x run_customer_services_tests.sh
chmod +x run_customers_tests.sh
chmod +x run_inserts_tests.sh
chmod +x run_orders_tests.sh
chmod +x run_products_tests.sh
chmod +x run_rules_tests.sh
chmod +x run_services_tests.sh
chmod +x run_shipping_tests.sh
chmod +x run_integration_tests.sh
chmod +x run_testcontainers_tests.sh

echo "All test scripts are now executable!"
echo ""
echo "You can run tests for a specific app with:"
echo "./run_<app>_tests.sh"
echo ""
echo "For example:"
echo "./run_materials_tests.sh"
echo ""
echo "Or run all tests with:"
echo "./run_docker_tests.sh"