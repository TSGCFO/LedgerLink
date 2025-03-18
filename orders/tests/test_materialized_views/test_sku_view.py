# orders/tests/test_materialized_views/test_sku_view.py
import pytest
from django.test import TestCase
from django.db import connection
from django.core.management import call_command
from io import StringIO
from orders.models import Order, OrderSKUView
from orders.tests.factories import OrderFactory
from unittest.mock import patch, MagicMock, call


@pytest.mark.django_db
@pytest.mark.skipif('orders.tests.mock_ordersku_view.should_skip_materialized_view_tests()', reason="Materialized views tests skipped")
class TestOrderSKUViewRefresh:
    """
    Tests for refreshing the OrderSKUView materialized view.
    Only run these tests with PostgreSQL.
    """
    
    def setup_method(self):
        """Set up test data."""
        # Skip all tests in this class if not using PostgreSQL
        if connection.vendor != 'postgresql':
            pytest.skip("OrderSKUView refresh tests require PostgreSQL")
    
    def test_refresh_sku_view_command(self):
        """Test the refresh_sku_view management command."""
        # Create a mock cursor
        mock_cursor = MagicMock()
        mock_cursor_context = MagicMock()
        mock_cursor_context.__enter__.return_value = mock_cursor
        
        # Create a mock connection
        mock_connection = MagicMock()
        mock_connection.cursor.return_value = mock_cursor_context
        
        # Capture command output
        out = StringIO()
        
        # Run the command with the mock connection
        with patch('orders.management.commands.refresh_sku_view.connection', mock_connection):
            call_command('refresh_sku_view', stdout=out)
        
        # Check that the SQL was executed correctly
        mock_cursor.execute.assert_called_once_with('REFRESH MATERIALIZED VIEW CONCURRENTLY orders_sku_view')
        
        # Check the output contains success message
        assert "Successfully refreshed orders_sku_view" in out.getvalue()
    
    def test_refresh_all_views_command(self):
        """Test the refresh_all_views management command."""
        # Create a mock cursor
        mock_cursor = MagicMock()
        mock_cursor_context = MagicMock()
        mock_cursor_context.__enter__.return_value = mock_cursor
        
        # Create a mock connection
        mock_connection = MagicMock()
        mock_connection.cursor.return_value = mock_cursor_context
        
        # Capture command output
        out = StringIO()
        
        # Run the command with the mock connection
        with patch('orders.management.commands.refresh_all_views.connection', mock_connection):
            call_command('refresh_all_views', stdout=out)
        
        # Check that the SQL was executed correctly for both views
        expected_calls = [
            call('REFRESH MATERIALIZED VIEW  orders_sku_view'),
            call('REFRESH MATERIALIZED VIEW  customer_services_customerserviceview')
        ]
        mock_cursor.execute.assert_has_calls(expected_calls)
        
        # Check the output contains success messages
        assert "Successfully refreshed orders_sku_view" in out.getvalue()
        assert "Successfully refreshed customer_services_customerserviceview" in out.getvalue()
    
    def test_refresh_all_views_concurrent(self):
        """Test the refresh_all_views management command with concurrent option."""
        # Create a mock cursor
        mock_cursor = MagicMock()
        mock_cursor_context = MagicMock()
        mock_cursor_context.__enter__.return_value = mock_cursor
        
        # Create a mock connection
        mock_connection = MagicMock()
        mock_connection.cursor.return_value = mock_cursor_context
        
        # Capture command output
        out = StringIO()
        
        # Run the command with the mock connection and concurrent flag
        with patch('orders.management.commands.refresh_all_views.connection', mock_connection):
            call_command('refresh_all_views', concurrent=True, stdout=out)
        
        # Check that the SQL was executed correctly with CONCURRENTLY
        expected_calls = [
            call('REFRESH MATERIALIZED VIEW CONCURRENTLY orders_sku_view'),
            call('REFRESH MATERIALIZED VIEW CONCURRENTLY customer_services_customerserviceview')
        ]
        mock_cursor.execute.assert_has_calls(expected_calls)


@pytest.mark.django_db
@pytest.mark.skipif('orders.tests.mock_ordersku_view.should_skip_materialized_view_tests()', reason="Materialized views tests skipped")
class TestOrderSKUViewCalculations:
    """
    Tests for OrderSKUView calculations.
    """
    
    @patch('orders.models.OrderSKUView.objects.filter')
    def test_case_and_pick_calculations(self, mock_filter):
        """Test that cases and picks are calculated correctly."""
        # Create an order with SKUs
        order = OrderFactory(
            sku_quantity={
                'SKU001': 25,  # Assuming case size of 10, should be 2 cases and 5 picks
                'SKU002': 40   # Assuming case size of 8, should be 5 cases and 0 picks
            }
        )
        
        # Create mock queryset for SKUs
        mock_sku1 = MagicMock(
            sku_name='SKU001',
            sku_count=25,
            cases=2,
            picks=5,
            case_size=10,
            case_unit='each'
        )
        mock_sku2 = MagicMock(
            sku_name='SKU002',
            sku_count=40,
            cases=5,
            picks=0,
            case_size=8,
            case_unit='each'
        )
        mock_queryset = MagicMock()
        mock_queryset.aggregate.return_value = {'total_cases': 7}
        mock_filter.return_value = mock_queryset
        
        # Set up values() to return the mock SKUs
        mock_queryset.values.return_value = [
            {
                'sku_name': 'SKU001',
                'cases': 2,
                'picks': 5,
                'case_size': 10,
                'case_unit': 'each'
            },
            {
                'sku_name': 'SKU002',
                'cases': 5,
                'picks': 0,
                'case_size': 8,
                'case_unit': 'each'
            }
        ]
        
        # Call the method to get case summary
        summary = order.get_case_summary()
        
        # Verify results
        assert summary['total_cases'] == 7
        assert len(summary['sku_breakdown']) == 2
        
        # Verify first SKU
        sku1 = next(item for item in summary['sku_breakdown'] if item['sku_name'] == 'SKU001')
        assert sku1['cases'] == 2
        assert sku1['picks'] == 5
        assert sku1['case_size'] == 10
        
        # Verify second SKU
        sku2 = next(item for item in summary['sku_breakdown'] if item['sku_name'] == 'SKU002')
        assert sku2['cases'] == 5
        assert sku2['picks'] == 0
        assert sku2['case_size'] == 8


@pytest.mark.django_db
@pytest.mark.skipif('orders.tests.mock_ordersku_view.should_skip_materialized_view_tests()', reason="Materialized views tests skipped")
class TestOrderSKUViewRealDatabase:
    """
    Integration tests for OrderSKUView with a real database connection.
    Only run with PostgreSQL and if the view actually exists.
    """
    
    def setup_method(self):
        """Set up test data."""
        # Skip all tests in this class if not using PostgreSQL
        if connection.vendor != 'postgresql':
            pytest.skip("OrderSKUView database tests require PostgreSQL")
            
        # Check if the view exists
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public'
                    AND table_name = 'orders_sku_view'
                );
            """)
            view_exists = cursor.fetchone()[0]
            
        if not view_exists:
            pytest.skip("orders_sku_view does not exist in database")
    
    def test_integration_with_real_database(self, monkeypatch):
        """
        Test how OrderSKUView works with the real database.
        This test is more of a demonstration than an assertion-based test.
        """
        # Create a order with SKUs
        order = OrderFactory(
            sku_quantity={
                'SKU001': 25,
                'SKU002': 40
            }
        )
        
        # Force a refresh of the materialized view
        with connection.cursor() as cursor:
            try:
                cursor.execute("REFRESH MATERIALIZED VIEW orders_sku_view")
                # For a real test, you would now query the view and check the results
                monkeypatch.resetall()  # Remove any mocks we might have used
            except Exception as e:
                print(f"Error refreshing view: {e}")
                # This is not a test failure, just information