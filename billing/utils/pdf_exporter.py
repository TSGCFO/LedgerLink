# billing/utils/pdf_exporter.py

from io import BytesIO
from django.http import HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph

class PDFExporter:

    def generate_pdf(self, invoice_data):
        """Generate a PDF for the given invoice data."""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        elements = []

        # Title
        styles = getSampleStyleSheet()
        elements.append(Paragraph(f"Invoice #{invoice_data['id']}", styles['Title']))

        # Customer Information
        elements.append(Paragraph(f"Customer: {invoice_data['customer']}", styles['Normal']))
        elements.append(Paragraph(f"Invoice Date: {invoice_data['invoice_date']}", styles['Normal']))

        # Table of services
        table_data = [["Service", "Cost"]]
        for detail in invoice_data['details']:
            table_data.append([detail['service'], f"${detail['cost']}"])

        table = Table(table_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(table)

        # Total Amount
        elements.append(Paragraph(f"Total Amount: ${invoice_data['total_cost']}", styles['Heading2']))

        doc.build(elements)
        buffer.seek(0)
        return HttpResponse(buffer, content_type='application/pdf')
