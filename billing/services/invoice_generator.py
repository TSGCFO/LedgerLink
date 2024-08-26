# billing/services/invoice_generator.py

from .billing_calculator import BillingCalculator
from billing.models import Invoice
from django.utils import timezone
from ..utils.pdf_exporter import PDFExporter

class InvoiceGenerator:

    def __init__(self, customer, orders):
        self.billing_calculator = BillingCalculator(customer, orders)
        self.total_cost, self.order_details = self.billing_calculator.calculate_total_billing()

    def generate_invoice(self):
        """Generate a structured invoice data."""
        invoice_data = {
            'customer': self.billing_calculator.customer,
            'invoice_date': timezone.now(),
            'total_cost': self.total_cost,
            'details': self.order_details,  # Already a list of dictionaries
        }
        return invoice_data

    def save_invoice(self, invoice_data):
        """(Optional) Save the generated invoice to the database."""
        invoice = Invoice(
            customer=invoice_data['customer'],
            total_amount=invoice_data['total_cost'],
            details=invoice_data['details']  # Save the list of dictionaries directly
        )
        invoice.save()
        return invoice

    def generate_pdf_invoice(self, invoice_data):
        """(Optional) Generate a PDF version of the invoice."""
        pdf_exporter = PDFExporter()
        pdf_file = pdf_exporter.generate_pdf(invoice_data)
        return pdf_file
