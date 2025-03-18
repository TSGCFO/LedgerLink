import unittest
from unittest.mock import patch, MagicMock
from decimal import Decimal
from django.test import SimpleTestCase
from ..utils.calculator import BillingCalculator


class CustomerServiceFilteringUnitTest(SimpleTestCase):
    """Unit tests for customer service filtering in BillingCalculator using mocks"""

    def setUp(self):
        """Set up test data for customer service filtering tests"""
        # Create mock customer services
        self.cs1 = MagicMock()
        self.cs1.id = 1
        self.cs1.service.id = 101
        self.cs1.service.service_name = "Single Service"
        self.cs1.service.charge_type = "single"
        self.cs1.unit_price = Decimal('100.00')
        
        self.cs2 = MagicMock()
        self.cs2.id = 2
        self.cs2.service.id = 102
        self.cs2.service.service_name = "Quantity Service"
        self.cs2.service.charge_type = "quantity"
        self.cs2.unit_price = Decimal('10.00')
        
        self.cs3 = MagicMock()
        self.cs3.id = 3
        self.cs3.service.id = 103
        self.cs3.service.service_name = "Case-based Service" 
        self.cs3.service.charge_type = "case_based_tier"
        self.cs3.unit_price = Decimal('50.00')
        
        # Mock order
        self.order = MagicMock()
        self.order.transaction_id = 12345
        self.order.close_date = "2023-01-15"
        self.order.reference_number = "REF12345"
        self.order.total_item_qty = 5
        
        # Mock customer services queryset
        self.all_customer_services = [self.cs1, self.cs2, self.cs3]
        
    @patch('Billing_V2.utils.calculator.CustomerService.objects.filter')
    @patch('Billing_V2.utils.calculator.Order.objects.filter')
    def test_filtering_with_specific_services(self, mock_order_filter, mock_cs_filter):
        """Test that customer service filtering works with specific services"""
        # Set up mocks
        mock_order_filter.return_value.select_related.return_value.order_by.return_value = [self.order]
        
        # Mock the first filter query
        mock_cs_initial_query = MagicMock()
        mock_cs_filter.return_value = mock_cs_initial_query
        
        # Mock the second filter query when specific service IDs are provided
        mock_cs_filtered_query = MagicMock()
        mock_cs_initial_query.filter.return_value = mock_cs_filtered_query
        
        # Set up the final select_related query to return only cs1 and cs3
        mock_cs_filtered_query.select_related.return_value = [self.cs1, self.cs3]
        
        # Create calculator with specific service IDs
        calculator = BillingCalculator(
            customer_id=1,
            start_date="2023-01-01",
            end_date="2023-01-31",
            customer_service_ids=[1, 3]  # Only cs1 and cs3
        )
        
        # Mock some methods to avoid database calls
        calculator.validate_input = MagicMock()
        calculator.calculate_service_cost = MagicMock(side_effect=[Decimal('100.00'), Decimal('50.00')])
        calculator.report.save = MagicMock()
        calculator.update_progress = MagicMock()
        
        # Generate report
        calculator.generate_report()
        
        # Verify the filtering was applied correctly
        mock_cs_initial_query.filter.assert_called_once_with(id__in=[1, 3])
        
    @patch('Billing_V2.utils.calculator.CustomerService.objects.filter')
    @patch('Billing_V2.utils.calculator.Order.objects.filter')
    def test_no_filtering_without_service_ids(self, mock_order_filter, mock_cs_filter):
        """Test that no filtering is applied when no customer_service_ids are provided"""
        # Set up mocks
        mock_order_filter.return_value.select_related.return_value.order_by.return_value = [self.order]
        
        # Mock the filter query to return all customer services
        mock_cs_query = MagicMock()
        mock_cs_filter.return_value = mock_cs_query
        mock_cs_query.select_related.return_value = self.all_customer_services
        
        # Create calculator without service IDs
        calculator = BillingCalculator(
            customer_id=1,
            start_date="2023-01-01",
            end_date="2023-01-31",
            customer_service_ids=None  # No filtering
        )
        
        # Mock some methods to avoid database calls
        calculator.validate_input = MagicMock()
        calculator.calculate_service_cost = MagicMock(side_effect=[
            Decimal('100.00'), Decimal('50.00'), Decimal('50.00')
        ])
        calculator.report.save = MagicMock()
        calculator.update_progress = MagicMock()
        
        # Generate report
        calculator.generate_report()
        
        # Verify no secondary filtering was applied
        mock_cs_query.filter.assert_not_called()
        
    @patch('Billing_V2.utils.calculator.CustomerService.objects.filter')
    @patch('Billing_V2.utils.calculator.Order.objects.filter')
    def test_empty_list_filtering(self, mock_order_filter, mock_cs_filter):
        """Test that empty service list results in no services being selected"""
        # Set up mocks
        mock_order_filter.return_value.select_related.return_value.order_by.return_value = [self.order]
        
        # Mock the initial filter query
        mock_cs_initial_query = MagicMock()
        mock_cs_filter.return_value = mock_cs_initial_query
        
        # Mock the second filter query when empty list is provided
        mock_cs_filtered_query = MagicMock()
        mock_cs_initial_query.filter.return_value = mock_cs_filtered_query
        
        # Return empty list from final select_related
        mock_cs_filtered_query.select_related.return_value = []
        
        # Create calculator with empty service ID list
        calculator = BillingCalculator(
            customer_id=1,
            start_date="2023-01-01",
            end_date="2023-01-31",
            customer_service_ids=[]  # Empty list
        )
        
        # Mock some methods to avoid database calls
        calculator.validate_input = MagicMock()
        calculator.calculate_service_cost = MagicMock()
        calculator.report.save = MagicMock()
        calculator.update_progress = MagicMock()
        
        # Generate report
        calculator.generate_report()
        
        # Verify the filtering was applied with empty list
        mock_cs_initial_query.filter.assert_called_once_with(id__in=[])
        # Check that calculate_service_cost was never called (no services)
        calculator.calculate_service_cost.assert_not_called()
        
    def test_metadata_stored_in_report(self):
        """Test that customer service IDs are stored in report metadata"""
        service_ids = [1, 3]
        
        # Create calculator with specific service IDs
        calculator = BillingCalculator(
            customer_id=1,
            start_date="2023-01-01",
            end_date="2023-01-31",
            customer_service_ids=service_ids
        )
        
        # Verify metadata was set correctly
        self.assertIn('selected_services', calculator.report.metadata)
        self.assertEqual(calculator.report.metadata['selected_services'], service_ids)


if __name__ == '__main__':
    unittest.main()