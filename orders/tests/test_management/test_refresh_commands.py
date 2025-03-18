# orders/tests/test_management/test_refresh_commands.py
import pytest
from django.test import TestCase
from django.core.management import call_command
from io import StringIO
from django.db import connection
from unittest.mock import patch, MagicMock, call
import logging


class TestManagementCommands(TestCase):
    """
    Test suite for the management commands.
    """
    
    def setUp(self):
        """Set up test data."""
        # Skip if not using PostgreSQL
        if connection.vendor != 'postgresql':
            self.skipTest("Management command tests require PostgreSQL")
    
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
        self.assertIn("Successfully refreshed orders_sku_view", out.getvalue())
    
    def test_refresh_sku_view_command_with_exception(self):
        """Test the error handling of refresh_sku_view management command."""
        # Create a mock cursor that raises an exception
        mock_cursor = MagicMock()
        mock_cursor.execute.side_effect = Exception("Test exception")
        mock_cursor_context = MagicMock()
        mock_cursor_context.__enter__.return_value = mock_cursor
        
        # Create a mock connection
        mock_connection = MagicMock()
        mock_connection.cursor.return_value = mock_cursor_context
        
        # Mock logger to test error logging
        mock_logger = MagicMock()
        
        # Capture command output
        out = StringIO()
        
        # Run the command with the mock connection
        with patch('orders.management.commands.refresh_sku_view.connection', mock_connection), \
             patch('orders.management.commands.refresh_sku_view.logger', mock_logger), \
             self.assertRaises(Exception):
            call_command('refresh_sku_view', stdout=out)
        
        # Check the output contains error message
        self.assertIn("Error refreshing orders_sku_view", out.getvalue())
        
        # Check that the logger was called with the error
        mock_logger.error.assert_called_once_with('Error refreshing orders_sku_view: Test exception')
    
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
        self.assertIn("Successfully refreshed orders_sku_view", out.getvalue())
        self.assertIn("Successfully refreshed customer_services_customerserviceview", out.getvalue())
    
    def test_refresh_all_views_command_with_exception(self):
        """Test the error handling of refresh_all_views management command."""
        # Create a mock cursor that raises an exception for the second view
        mock_cursor = MagicMock()
        mock_cursor.execute.side_effect = [None, Exception("Test exception")]
        mock_cursor_context = MagicMock()
        mock_cursor_context.__enter__.return_value = mock_cursor
        
        # Create a mock connection
        mock_connection = MagicMock()
        mock_connection.cursor.return_value = mock_cursor_context
        
        # Mock logger to test error logging
        mock_logger = MagicMock()
        
        # Capture command output
        out = StringIO()
        
        # Run the command with the mock connection
        with patch('orders.management.commands.refresh_all_views.connection', mock_connection), \
             patch('orders.management.commands.refresh_all_views.logger', mock_logger):
            call_command('refresh_all_views', stdout=out)
        
        # Check the output contains success and error messages
        self.assertIn("Successfully refreshed orders_sku_view", out.getvalue())
        self.assertIn("Error refreshing customer_services_customerserviceview", out.getvalue())
        
        # Check that the logger was called with the error
        mock_logger.error.assert_called_once_with('Error refreshing customer_services_customerserviceview: Test exception')
    
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
        
        # Check the output contains success messages
        self.assertIn("Successfully refreshed orders_sku_view", out.getvalue())
        self.assertIn("Successfully refreshed customer_services_customerserviceview", out.getvalue())