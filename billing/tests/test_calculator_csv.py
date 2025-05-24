import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime
from decimal import Decimal

from Billing_V2.utils.calculator import BillingCalculator, generate_billing_report

class TestBillingCalculatorCSV(unittest.TestCase):
    def test_to_csv_basic(self):
        calc = BillingCalculator(customer_id=1, start_date=datetime(2023, 1, 1), end_date=datetime(2023, 1, 31))
        order = MagicMock()
        order.transaction_id = 1
        order.reference_number = "REF1"
        order.close_date = datetime(2023, 1, 2)

        service_cost = MagicMock()
        service_cost.service_id = 10
        service_cost.service_name = "Test Service"
        service_cost.amount = Decimal("5.00")

        order_cost = MagicMock()
        order_cost.order = order
        order_cost.service_costs.all.return_value = [service_cost]

        report = MagicMock()
        report.order_costs.all.return_value = [order_cost]
        report.service_totals = {10: {"service_name": "Test Service", "amount": Decimal("5.00")}}
        report.total_amount = Decimal("5.00")

        calc.report = report

        csv_output = calc.to_csv()
        expected = [
            "order_id,reference_number,date,service_id,service_name,amount",
            '1,"REF1",2023-01-02,10,"Test Service",5.00',
            "",
            "SUMMARY",
            "service_id,service_name,total_amount",
            '10,"Test Service",5.00',
            "",
            'TOTAL,"",5.00'
        ]
        self.assertEqual(csv_output.splitlines(), expected)

class TestGenerateBillingReportCSVPath(unittest.TestCase):
    @patch('Billing_V2.utils.calculator.BillingCalculator')
    def test_generate_billing_report_csv(self, mock_calc_cls):
        instance = MagicMock()
        mock_calc_cls.return_value = instance
        instance.generate_report.return_value = MagicMock()
        instance.to_csv.return_value = 'csv-data'

        result = generate_billing_report(1, '2023-01-01', '2023-01-31', 'csv')

        self.assertEqual(result, 'csv-data')
        instance.to_csv.assert_called_once()
