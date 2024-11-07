# billing/services/report_exporter.py

import pandas as pd
from io import BytesIO
from django.http import HttpResponse
from ..utils.pdf_generator import PDFExporter

class ReportExporter:

    def export_to_pdf(self, report_data):
        """Export a detailed report to PDF."""
        pdf_exporter = PDFExporter()
        pdf_file = pdf_exporter.generate_pdf(report_data)
        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename=billing_report.pdf'
        return response

    def export_to_excel(self, report_data):
        """Export a detailed report to Excel."""
        df = pd.DataFrame(report_data)

        # Create a BytesIO object to store the Excel file
        excel_file = BytesIO()

        # Use ExcelWriter with engine='xlsxwriter' and the BytesIO object
        with pd.ExcelWriter(excel_file, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Billing Report')

            # Access the XlsxWriter workbook and worksheet objects
            workbook = writer.book
            worksheet = writer.sheets['Billing Report']

            # Add any additional formatting if needed
            # For example, you can adjust column widths
            for i, col in enumerate(df.columns):
                column_width = max(df[col].astype(str).map(len).max(), len(col)) + 2
                worksheet.set_column(i, i, column_width)

        # Set the BytesIO object's file pointer to the beginning
        excel_file.seek(0)

        # Create the HttpResponse with the Excel file
        response = HttpResponse(excel_file.getvalue(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=billing_report.xlsx'
        return response