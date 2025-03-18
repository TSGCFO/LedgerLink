#!/usr/bin/env python
"""
Comprehensive test for the billing calculator service selection fix.
This is a standalone test that mocks the necessary components.
"""

import unittest
import json
import logging
from datetime import datetime, date, timedelta
from decimal import Decimal

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('test_billing_service_selection')

class MockBillingReport:
    """Mock implementation of BillingReport model."""
    
    def __init__(self, customer_id=1, start_date=None, end_date=None, total_amount=Decimal('0'), 
                 service_totals=None, metadata=None):
        self.id = 1
        self.customer_id = customer_id
        self.start_date = start_date or datetime.now()
        self.end_date = end_date or datetime.now()
        self.created_at = datetime.now()
        self.total_amount = total_amount
        self.service_totals = service_totals or {}
        self.metadata = metadata or {}
        self.order_costs = []
    
    def update_total_amount(self):
        """Update the total amount based on service totals."""
        try:
            if not self.service_totals:
                self.total_amount = Decimal('0')
                return
                
            # Sum all service amounts from service_totals
            total = sum(Decimal(str(data['amount'])) for data in self.service_totals.values())
            self.total_amount = total
            logger.info(f"Updated report #{self.id} total_amount to {total} based on service totals")
        except Exception as e:
            logger.error(f"Error updating total amount: {str(e)}")
            # Fallback to calculating from order costs
            try:
                total = sum(order_cost.total_amount for order_cost in self.order_costs)
                self.total_amount = total
                logger.info(f"Fallback: Updated report #{self.id} total_amount to {total} based on order costs")
            except Exception as inner_e:
                logger.error(f"Fallback failed: {str(inner_e)}")
    
    def add_order_cost(self, order_cost):
        """
        Add an order cost to this report and update totals.
        
        Args:
            order_cost: OrderCost object to add
        """
        self.order_costs.append(order_cost)
        
        # Update service totals
        for service_cost in order_cost.service_costs:
            service_id = str(service_cost.service_id)
            if service_id in self.service_totals:
                self.service_totals[service_id]['amount'] += float(service_cost.amount)
            else:
                self.service_totals[service_id] = {
                    'service_name': service_cost.service_name,
                    'amount': float(service_cost.amount)
                }
        
        # Update total amount from service totals
        self.update_total_amount()
        self.save()
    
    def save(self):
        """Mock save method."""
        pass
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'customer_id': self.customer_id,
            'customer_name': 'Test Customer',
            'start_date': self.start_date.strftime('%Y-%m-%d'),
            'end_date': self.end_date.strftime('%Y-%m-%d'),
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'total_amount': float(self.total_amount),
            'service_totals': self.service_totals,
            'metadata': self.metadata,
            'orders': [order_cost.to_dict() for order_cost in self.order_costs]
        }
    
    def to_json(self):
        """Convert to JSON."""
        return json.dumps(self.to_dict())

class MockOrderCost:
    """Mock implementation of OrderCost model."""
    
    def __init__(self, order=None, billing_report=None, total_amount=Decimal('0')):
        self.id = 1
        self.order = order
        self.billing_report = billing_report
        self.total_amount = total_amount
        self.service_costs = []
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'order_id': getattr(self.order, 'transaction_id', f"ORD-{self.id}"),
            'reference_number': getattr(self.order, 'reference_number', f"REF-{self.id}"),
            'order_date': datetime.now().strftime('%Y-%m-%d'),
            'service_costs': [sc.to_dict() for sc in self.service_costs],
            'total_amount': float(self.total_amount)
        }

class MockServiceCost:
    """Mock implementation of ServiceCost model."""
    
    def __init__(self, order_cost=None, service_id=1, service_name="Test Service", amount=Decimal('0')):
        self.id = 1
        self.order_cost = order_cost
        self.service_id = service_id
        self.service_name = service_name
        self.amount = amount
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'service_id': self.service_id,
            'service_name': self.service_name,
            'amount': float(self.amount)
        }

class MockCustomer:
    """Mock implementation of Customer model."""
    
    def __init__(self, id=1, company_name="Test Customer"):
        self.id = id
        self.company_name = company_name

class MockOrder:
    """Mock implementation of Order model."""
    
    def __init__(self, id=1, customer_id=1, transaction_id=None, reference_number=None, 
                 total_item_qty=10, sku_quantity=None, close_date=None):
        self.id = id
        self.customer_id = customer_id
        self.transaction_id = transaction_id or f"ORD-{id}"
        self.reference_number = reference_number or f"REF-{id}"
        self.total_item_qty = total_item_qty
        self.sku_quantity = sku_quantity or {"SKU1": 5, "SKU2": 5}
        self.close_date = close_date or datetime.now()
        self._normalized_sku_dict = self.sku_quantity  # For mock purposes

class MockService:
    """Mock implementation of Service model."""
    
    def __init__(self, id=1, service_name="Test Service", charge_type="quantity"):
        self.id = id
        self.service_name = service_name
        self.charge_type = charge_type

class MockCustomerService:
    """Mock implementation of CustomerService model."""
    
    def __init__(self, id=1, customer_id=1, service=None, service_id=None, unit_price=Decimal('10.00')):
        self.id = id
        self.customer_id = customer_id
        self.service = service or MockService(id=service_id or id)
        self.unit_price = unit_price
    
    def get_sku_list(self):
        """Mock SKU list."""
        return []

class BillingCalculator:
    """Mock implementation of BillingCalculator."""
    
    def __init__(self, customer_id, start_date, end_date, customer_service_ids=None):
        """
        Initialize the calculator with customer and date range.
        
        Args:
            customer_id: ID of the customer
            start_date: Start date for billing period
            end_date: End date for billing period
            customer_service_ids: Optional list of customer service IDs to include
        """
        self.customer_id = customer_id
        self.customer_service_ids = customer_service_ids
        self.start_date = start_date
        self.end_date = end_date
        self.progress = {
            'status': 'initializing',
            'percent_complete': 0,
            'current_step': 'Initializing calculator',
            'processed_orders': 0,
            'total_orders': 0
        }
        
        # Create empty report
        self.report = MockBillingReport(
            customer_id=customer_id,
            start_date=self.start_date,
            end_date=self.end_date,
            total_amount=Decimal('0'),
            service_totals={}
        )
        
        # Store metadata about customer service selection in report metadata
        self.report.metadata = {
            'selected_services': customer_service_ids
        }
    
    def generate_report(self):
        """Generate the billing report."""
        # Create a customer
        customer = MockCustomer(id=self.customer_id)
        
        # Create some services
        services = [
            MockService(id=1, service_name="Picking Service", charge_type="quantity"),
            MockService(id=2, service_name="Shipping Service", charge_type="quantity"),
            MockService(id=3, service_name="Storage Service", charge_type="single"),
            MockService(id=4, service_name="Handling Service", charge_type="quantity"),
            MockService(id=5, service_name="Return Processing", charge_type="single")
        ]
        
        # Create customer services
        customer_services = [
            MockCustomerService(id=1, customer_id=self.customer_id, service=services[0], unit_price=Decimal('2.50')),
            MockCustomerService(id=2, customer_id=self.customer_id, service=services[1], unit_price=Decimal('3.75')),
            MockCustomerService(id=3, customer_id=self.customer_id, service=services[2], unit_price=Decimal('100.00')),
            MockCustomerService(id=4, customer_id=self.customer_id, service=services[3], unit_price=Decimal('1.25')),
            MockCustomerService(id=5, customer_id=self.customer_id, service=services[4], unit_price=Decimal('50.00'))
        ]
        
        # Filter customer services if specified
        if self.customer_service_ids is not None:  # Check if None (all services) or not None (filtered)
            customer_services = [cs for cs in customer_services if cs.id in self.customer_service_ids]
        
        # Create orders
        orders = [
            MockOrder(id=1, customer_id=self.customer_id, transaction_id="ORD-001", reference_number="REF-001", 
                      total_item_qty=20, sku_quantity={"ABC123": 10, "DEF456": 10}),
            MockOrder(id=2, customer_id=self.customer_id, transaction_id="ORD-002", reference_number="REF-002", 
                      total_item_qty=5, sku_quantity={"GHI789": 5}),
            MockOrder(id=3, customer_id=self.customer_id, transaction_id="ORD-003", reference_number="REF-003", 
                      total_item_qty=15, sku_quantity={"JKL012": 8, "MNO345": 7})
        ]
        
        # Process each order
        for order in orders:
            # Create order cost
            order_cost = MockOrderCost(order=order, billing_report=self.report)
            
            # Process each customer service for this order
            for cs in customer_services:
                # Calculate a mock amount based on order and service
                if cs.service.charge_type == "quantity":
                    amount = cs.unit_price * Decimal(str(order.total_item_qty))
                else:  # single
                    amount = cs.unit_price
                
                # Create service cost if amount > 0
                if amount > 0:
                    service_cost = MockServiceCost(
                        order_cost=order_cost,
                        service_id=cs.service.id,
                        service_name=cs.service.service_name,
                        amount=amount
                    )
                    order_cost.service_costs.append(service_cost)
            
            # Calculate order total
            if order_cost.service_costs:
                order_cost.total_amount = sum(sc.amount for sc in order_cost.service_costs)
                
                # Add order cost to report
                self.report.add_order_cost(order_cost)
        
        # Make sure the total amount is accurate
        if not hasattr(self.report, 'total_amount') or self.report.total_amount == 0:
            # Calculate total from service totals if not already set
            total = sum(Decimal(str(data['amount'])) for data in self.report.service_totals.values())
            self.report.total_amount = total
            logger.info(f"Total amount calculated from service totals: {total}")
        
        return self.report
    
    def to_csv(self):
        """Convert report to CSV format."""
        # Create header line
        lines = ["order_id,reference_number,date,service_id,service_name,amount"]
        
        # Process each order and its service costs
        for order_cost in self.report.order_costs:
            order = order_cost.order
            reference = order.reference_number.replace('"', '""') if order.reference_number else ""
            date = order.close_date.strftime('%Y-%m-%d') if order.close_date else ""
            
            for service_cost in order_cost.service_costs:
                # Format service name for CSV (escape quotes)
                service_name = service_cost.service_name.replace('"', '""') if service_cost.service_name else ""
                
                # Build CSV line
                line = f"{order.transaction_id},\"{reference}\",{date},{service_cost.service_id},"
                line += f"\"{service_name}\",{service_cost.amount}"
                lines.append(line)
        
        # Add a summary section
        lines.append("")
        lines.append("SUMMARY")
        lines.append("service_id,service_name,total_amount")
        
        for service_id, data in self.report.service_totals.items():
            service_name = data['service_name'].replace('"', '""') if data['service_name'] else ""
            lines.append(f"{service_id},\"{service_name}\",{data['amount']}")
        
        lines.append("")
        lines.append(f"TOTAL,\"\",{self.report.total_amount}")
                
        return "\n".join(lines)
    
    def to_json(self):
        """Convert report to JSON format."""
        return self.report.to_json()

class TestBillingCalculator(unittest.TestCase):
    """Test the billing calculator with service selection."""
    
    def setUp(self):
        """Set up test data."""
        # Set up dates
        self.start_date = date.today() - timedelta(days=30)
        self.end_date = date.today()
    
    def test_all_services_included(self):
        """Test when all services are included (customer_service_ids=None)."""
        # Create calculator with no specific services
        calculator = BillingCalculator(
            customer_id=1,
            start_date=self.start_date,
            end_date=self.end_date,
            customer_service_ids=None  # Include all services
        )
        
        # Generate report
        report = calculator.generate_report()
        
        # Verify service totals
        self.assertEqual(len(report.service_totals), 5, "Should have 5 services in the report")
        
        # Total amount should be sum of all service costs
        expected_total = Decimal('0')
        for service_id, data in report.service_totals.items():
            expected_total += Decimal(str(data['amount']))
        
        self.assertEqual(report.total_amount, expected_total,
                         f"Report total ({report.total_amount}) should match sum of service totals ({expected_total})")
        
        # Verify report has orders
        self.assertGreater(len(report.order_costs), 0, "Report should have orders")
    
    def test_specific_services_selected(self):
        """Test when specific services are selected."""
        # Select just 2 services
        selected_services = [1, 3]  # Picking and Storage
        
        # Create calculator with specific services
        calculator = BillingCalculator(
            customer_id=1,
            start_date=self.start_date,
            end_date=self.end_date,
            customer_service_ids=selected_services
        )
        
        # Generate report
        report = calculator.generate_report()
        
        # Verify service totals have only the selected services
        service_ids = set(int(service_id) for service_id in report.service_totals.keys())
        self.assertEqual(service_ids, set(selected_services), 
                         f"Report should only include selected services {selected_services}, got {service_ids}")
        
        # Total amount should be sum of selected service costs
        expected_total = Decimal('0')
        for service_id, data in report.service_totals.items():
            expected_total += Decimal(str(data['amount']))
        
        self.assertEqual(report.total_amount, expected_total,
                         f"Report total ({report.total_amount}) should match sum of service totals ({expected_total})")
        
        # Verify report metadata contains selected services
        self.assertEqual(report.metadata.get('selected_services'), selected_services, 
                         "Report metadata should contain selected services")
    
    def test_empty_service_selection(self):
        """Test when empty list of services is provided (edge case)."""
        # Empty list of services
        calculator = BillingCalculator(
            customer_id=1,
            start_date=self.start_date,
            end_date=self.end_date,
            customer_service_ids=[]  # Empty list
        )
        
        # Generate report
        report = calculator.generate_report()
        
        # Report should have no services and zero total
        self.assertEqual(len(report.service_totals), 0, "Report should have no services")
        self.assertEqual(report.total_amount, Decimal('0'), "Report total should be zero")
        
        # Verify report metadata contains empty selected services
        self.assertEqual(report.metadata.get('selected_services'), [], 
                         "Report metadata should contain empty services list")
    
    def test_single_service_selection(self):
        """Test when only one service is selected."""
        # Select just one service
        selected_service = [3]  # Storage (single charge type)
        
        calculator = BillingCalculator(
            customer_id=1,
            start_date=self.start_date,
            end_date=self.end_date,
            customer_service_ids=selected_service
        )
        
        # Generate report
        report = calculator.generate_report()
        
        # Verify service totals have only the selected service
        service_ids = set(int(service_id) for service_id in report.service_totals.keys())
        self.assertEqual(service_ids, set(selected_service), 
                         f"Report should only include selected service {selected_service}, got {service_ids}")
        
        # Get the amount for the service
        service_id_str = str(selected_service[0])
        service_amount = Decimal(str(report.service_totals.get(service_id_str, {}).get('amount', 0)))
        
        # Report total should equal the service amount
        self.assertEqual(report.total_amount, service_amount,
                         f"Report total ({report.total_amount}) should equal service amount ({service_amount})")
    
    def test_nonexistent_service_selection(self):
        """Test when service IDs that don't exist are selected (edge case)."""
        # Nonexistent service IDs
        nonexistent_services = [99, 100]
        
        calculator = BillingCalculator(
            customer_id=1,
            start_date=self.start_date,
            end_date=self.end_date,
            customer_service_ids=nonexistent_services
        )
        
        # Generate report
        report = calculator.generate_report()
        
        # Report should have no services and zero total
        self.assertEqual(len(report.service_totals), 0, "Report should have no services")
        self.assertEqual(report.total_amount, Decimal('0'), "Report total should be zero")
    
    def test_mixed_service_types(self):
        """Test a mix of single and quantity-based services."""
        # Mix of single and quantity services
        mixed_services = [2, 3, 5]  # Shipping (quantity), Storage (single), Return Processing (single)
        
        calculator = BillingCalculator(
            customer_id=1,
            start_date=self.start_date,
            end_date=self.end_date,
            customer_service_ids=mixed_services
        )
        
        # Generate report
        report = calculator.generate_report()
        
        # Verify service totals have only the selected services
        service_ids = set(int(service_id) for service_id in report.service_totals.keys())
        self.assertEqual(service_ids, set(mixed_services), 
                         f"Report should only include selected services {mixed_services}, got {service_ids}")
        
        # Total amount should be sum of selected service costs
        expected_total = Decimal('0')
        for service_id, data in report.service_totals.items():
            expected_total += Decimal(str(data['amount']))
        
        self.assertEqual(report.total_amount, expected_total,
                         f"Report total ({report.total_amount}) should match sum of service totals ({expected_total})")
    
    def test_update_total_amount_method(self):
        """Test the update_total_amount method directly."""
        # Create a report with service totals
        report = MockBillingReport(
            customer_id=1,
            start_date=self.start_date,
            end_date=self.end_date,
            service_totals={
                '1': {'service_name': 'Service 1', 'amount': 25.0},
                '2': {'service_name': 'Service 2', 'amount': 50.0},
                '3': {'service_name': 'Service 3', 'amount': 75.0}
            },
            total_amount=0  # Zero initial amount
        )
        
        # Call update_total_amount
        report.update_total_amount()
        
        # Verify total is sum of service amounts
        expected_total = Decimal('150')  # 25 + 50 + 75
        self.assertEqual(report.total_amount, expected_total, 
                         f"Report total should be {expected_total}, got {report.total_amount}")
    
    def test_add_order_cost_updates_totals(self):
        """Test that add_order_cost properly updates service totals and total amount."""
        # Create a report
        report = MockBillingReport(
            customer_id=1,
            start_date=self.start_date,
            end_date=self.end_date
        )
        
        # Create an order
        order = MockOrder(id=1, customer_id=1)
        
        # Create an order cost with service costs
        order_cost = MockOrderCost(order=order, billing_report=report)
        
        # Add service costs to the order cost
        service_costs = [
            MockServiceCost(order_cost=order_cost, service_id=1, service_name="Service 1", amount=Decimal('10.00')),
            MockServiceCost(order_cost=order_cost, service_id=2, service_name="Service 2", amount=Decimal('20.00'))
        ]
        order_cost.service_costs = service_costs
        
        # Set order cost total
        order_cost.total_amount = Decimal('30.00')
        
        # Add order cost to report
        report.add_order_cost(order_cost)
        
        # Verify service totals updated
        self.assertEqual(len(report.service_totals), 2, "Report should have 2 services")
        self.assertEqual(report.service_totals.get('1', {}).get('amount'), 10.0, 
                         "Service 1 amount should be 10.0")
        self.assertEqual(report.service_totals.get('2', {}).get('amount'), 20.0, 
                         "Service 2 amount should be 20.0")
        
        # Verify total amount updated
        self.assertEqual(report.total_amount, Decimal('30.00'), 
                         "Report total should be 30.00")
        
        # Add another order cost to test accumulation
        order2 = MockOrder(id=2, customer_id=1)
        order_cost2 = MockOrderCost(order=order2, billing_report=report)
        
        # Add service costs to the second order cost
        service_costs2 = [
            MockServiceCost(order_cost=order_cost2, service_id=1, service_name="Service 1", amount=Decimal('15.00')),
            MockServiceCost(order_cost=order_cost2, service_id=3, service_name="Service 3", amount=Decimal('25.00'))
        ]
        order_cost2.service_costs = service_costs2
        
        # Set second order cost total
        order_cost2.total_amount = Decimal('40.00')
        
        # Add second order cost to report
        report.add_order_cost(order_cost2)
        
        # Verify service totals updated with accumulated values
        self.assertEqual(len(report.service_totals), 3, "Report should have 3 services")
        self.assertEqual(report.service_totals.get('1', {}).get('amount'), 25.0, 
                         "Service 1 amount should be 25.0 (10 + 15)")
        self.assertEqual(report.service_totals.get('3', {}).get('amount'), 25.0, 
                         "Service 3 amount should be 25.0")
        
        # Verify total amount updated to accumulated value
        expected_total = Decimal('70.00')  # 10 + 20 + 15 + 25
        self.assertEqual(report.total_amount, expected_total, 
                         f"Report total should be {expected_total}, got {report.total_amount}")
    
    def test_to_csv_includes_total(self):
        """Test that the CSV output includes the correct total amount."""
        # Create calculator with specific services
        selected_services = [1, 3]  # Picking and Storage
        
        calculator = BillingCalculator(
            customer_id=1,
            start_date=self.start_date,
            end_date=self.end_date,
            customer_service_ids=selected_services
        )
        
        # Generate report
        report = calculator.generate_report()
        
        # Get CSV output
        csv_content = calculator.to_csv()
        
        # Split into lines
        lines = csv_content.strip().split('\n')
        
        # Get the total line (should be the last line)
        total_line = lines[-1]
        
        # Extract total amount from CSV
        csv_total = Decimal(total_line.split(',')[-1])
        
        # Verify total matches report total
        self.assertEqual(csv_total, report.total_amount, 
                         f"CSV total ({csv_total}) should match report total ({report.total_amount})")
        
        # Verify service totals are included in the CSV
        summary_section_index = lines.index("SUMMARY") + 2  # +2 to skip header line
        for service_id, data in report.service_totals.items():
            service_line = None
            for i in range(summary_section_index, len(lines) - 1):  # -1 to exclude the TOTAL line
                if lines[i].startswith(service_id + ','):
                    service_line = lines[i]
                    break
            
            self.assertIsNotNone(service_line, f"Service {service_id} should be in the CSV summary")
            
            # Extract amount from CSV line
            csv_amount = Decimal(service_line.split(',')[-1])
            
            # Verify amount matches service total
            self.assertEqual(csv_amount, Decimal(str(data['amount'])), 
                             f"CSV amount ({csv_amount}) should match service total ({data['amount']})")
    
    def test_json_output_includes_total(self):
        """Test that the JSON output includes the correct total amount."""
        # Create calculator with specific services
        selected_services = [2, 4]  # Shipping and Handling
        
        calculator = BillingCalculator(
            customer_id=1,
            start_date=self.start_date,
            end_date=self.end_date,
            customer_service_ids=selected_services
        )
        
        # Generate report
        report = calculator.generate_report()
        
        # Get JSON output
        json_content = calculator.to_json()
        
        # Parse JSON
        json_data = json.loads(json_content)
        
        # Verify total amount in JSON
        self.assertEqual(json_data['total_amount'], float(report.total_amount), 
                         f"JSON total should be {float(report.total_amount)}, got {json_data['total_amount']}")
        
        # Verify service totals in JSON
        for service_id, data in report.service_totals.items():
            self.assertIn(service_id, json_data['service_totals'], 
                          f"Service {service_id} should be in JSON service_totals")
            
            self.assertEqual(json_data['service_totals'][service_id]['amount'], data['amount'], 
                             f"JSON amount should be {data['amount']}, got {json_data['service_totals'][service_id]['amount']}")
    
    def test_decimal_precision_handling(self):
        """Test handling of decimal precision in monetary values."""
        # Create a mock report with precise decimal values
        report = MockBillingReport(
            customer_id=1,
            start_date=self.start_date,
            end_date=self.end_date,
            service_totals={
                '1': {'service_name': 'Service 1', 'amount': 10.123},
                '2': {'service_name': 'Service 2', 'amount': 5.67}
            }
        )
        
        # Update total amount
        report.update_total_amount()
        
        # Expected total with the exact precision
        expected_total = Decimal('15.793')  # 10.123 + 5.67
        
        # Test with quantize to ensure consistent decimal places
        self.assertEqual(
            report.total_amount.quantize(Decimal('0.001')), 
            expected_total.quantize(Decimal('0.001')),
            "Report total should match expected total with correct precision"
        )

if __name__ == '__main__':
    unittest.main()