# billing/services/report_exporter.py

import pandas as pd
from io import BytesIO
from django.http import HttpResponse
from ..utils.rule_applier import PDFExporter

class ReportExporter:

    def export_to_pdf(self, report_data):
        """Export a detailed report to PDF."""
        pdf_exporter = PDFExporter()
        pdf_file = pdf_exporter.generate_pdf(report_data)
        return pdf_file

    def export_to_excel(self, report_data):
        """Export a detailed report to Excel."""
        output = BytesIO()
        df = pd.DataFrame(report_data)
        writer = pd.ExcelWriter(output, engine='xlsxwriter')
        df.to_excel(writer, index=False, sheet_name='Billing Report')
        writer.save()
        output.seek(0)
        response = HttpResponse(output, content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename=billing_report.xlsx'
        return response
