from django.views.generic import TemplateView
from django.http import JsonResponse, HttpResponse
from django.core.exceptions import ValidationError
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .forms import BillingReportForm
from .billing_calculator import generate_billing_report
from .models import BillingReport, Customer
from django.core.serializers.json import DjangoJSONEncoder
from datetime import datetime
import json
import logging
import pandas as pd
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
import xlsxwriter

logger = logging.getLogger(__name__)

def generate_excel_report(report_data):
    """Generate Excel report with proper formatting"""
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet('Billing Report')

    # Add formats
    header_format = workbook.add_format({
        'bold': True,
        'bg_color': '#4B8BBE',
        'font_color': 'white',
        'border': 1
    })
    
    cell_format = workbook.add_format({
        'border': 1
    })
    
    currency_format = workbook.add_format({
        'border': 1,
        'num_format': '$#,##0.00'
    })

    # Write headers
    headers = ['Order ID', 'Services', 'Amount', 'Date']
    for col, header in enumerate(headers):
        worksheet.write(0, col, header, header_format)

    # Write data
    row = 1
    for order in report_data.get('orders', []):
        worksheet.write(row, 0, order['order_id'], cell_format)
        
        services = ', '.join([
            f"{service['service_name']}: ${service['amount']}"
            for service in order['services']
        ])
        worksheet.write(row, 1, services, cell_format)
        
        worksheet.write(row, 2, float(order['total_amount']), currency_format)
        worksheet.write(row, 3, order.get('date', ''), cell_format)
        row += 1

    # Write totals
    worksheet.write(row + 1, 1, 'Total Amount:', header_format)
    worksheet.write(row + 1, 2, float(report_data['total_amount']), currency_format)

    # Adjust column widths
    worksheet.set_column(0, 0, 15)  # Order ID
    worksheet.set_column(1, 1, 50)  # Services
    worksheet.set_column(2, 2, 15)  # Amount
    worksheet.set_column(3, 3, 20)  # Date

    workbook.close()
    output.seek(0)
    return output

def generate_pdf_report(report_data):
    """Generate PDF report with proper formatting"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()

    # Add title
    title = Paragraph(f"Billing Report for {report_data.get('customer_name', 'Customer')}", styles['Heading1'])
    elements.append(title)
    elements.append(Paragraph(f"Period: {report_data.get('start_date')} to {report_data.get('end_date')}", styles['Normal']))
    elements.append(Paragraph("<br/><br/>", styles['Normal']))

    # Prepare table data
    table_data = [['Order ID', 'Services', 'Amount', 'Date']]
    
    for order in report_data.get('orders', []):
        services = ', '.join([
            f"{service['service_name']}: ${service['amount']}"
            for service in order['services']
        ])
        table_data.append([
            str(order['order_id']),
            services,
            f"${order['total_amount']}",
            order.get('date', '')
        ])

    # Add total row
    table_data.append(['', 'Total Amount:', f"${report_data['total_amount']}", ''])

    # Create table
    table = Table(table_data, colWidths=[80, 250, 100, 100])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.blue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, -1), (-1, -1), colors.grey),
        ('TEXTCOLOR', (0, -1), (-1, -1), colors.whitesmoke),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, -1), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ALIGN', (2, 1), (2, -1), 'RIGHT'),
    ]))
    
    elements.append(table)
    doc.build(elements)
    buffer.seek(0)
    return buffer

def parse_date(date_str):
    """Parse date string to YYYY-MM-DD format"""
    try:
        # Try parsing ISO format
        date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return date.strftime('%Y-%m-%d')
    except (ValueError, AttributeError):
        try:
            # Try parsing other common formats
            date = datetime.strptime(date_str, '%Y-%m-%d')
            return date.strftime('%Y-%m-%d')
        except (ValueError, AttributeError):
            raise ValidationError(f"Invalid date format: {date_str}. Expected format: YYYY-MM-DD")

@method_decorator([ensure_csrf_cookie, csrf_exempt], name='dispatch')
class BillingReportView(TemplateView):
    template_name = 'billing/billing_report.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = BillingReportForm()
        return context

@method_decorator(csrf_exempt, name='dispatch')
class BillingReportListView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        try:
            reports = BillingReport.objects.select_related('customer').all()
            
            # Convert reports to list of dictionaries
            report_list = []
            for report in reports:
                report_dict = {
                    'id': report.id,
                    'customer': report.customer_id,
                    'customer_details': {
                        'id': report.customer.id,
                        'company_name': report.customer.company_name,
                    },
                    'start_date': report.start_date,
                    'end_date': report.end_date,
                    'generated_at': report.generated_at,
                    'total_amount': str(report.total_amount),  # Convert Decimal to string
                    'report_data': report.report_data
                }
                report_list.append(report_dict)

            return Response({
                'success': True,
                'data': report_list,
                'count': len(report_list)
            })
        except Exception as e:
            logger.error(f"Error fetching billing reports: {str(e)}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@method_decorator(csrf_exempt, name='dispatch')
class GenerateReportAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        try:
            logger.info(f"Received data: {request.data}")

            customer_id = request.data.get('customer')
            start_date = request.data.get('start_date')
            end_date = request.data.get('end_date')
            output_format = request.data.get('output_format', 'preview')

            if not all([customer_id, start_date, end_date]):
                missing_params = []
                if not customer_id: missing_params.append('customer')
                if not start_date: missing_params.append('start_date')
                if not end_date: missing_params.append('end_date')
                error_msg = f"Missing required parameters: {', '.join(missing_params)}"
                logger.error(error_msg)
                return Response(
                    {"error": error_msg},
                    status=status.HTTP_400_BAD_REQUEST
                )

            try:
                # Parse and validate dates
                try:
                    start_date = parse_date(start_date)
                    end_date = parse_date(end_date)
                except ValidationError as e:
                    return Response(
                        {"error": str(e)},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                customer_id = int(customer_id)
            except (TypeError, ValueError):
                error_msg = f"Invalid customer format: {customer_id}"
                logger.error(error_msg)
                return Response(
                    {"error": error_msg},
                    status=status.HTTP_400_BAD_REQUEST
                )

            try:
                # Get customer details
                customer = Customer.objects.get(id=customer_id)
                
                # Generate report data
                report_data = generate_billing_report(
                    customer_id=customer_id,
                    start_date=start_date,
                    end_date=end_date,
                    output_format='preview'
                )
                
                # Ensure report_data is a dictionary with required fields
                if not isinstance(report_data, dict):
                    report_data = {
                        'orders': [],
                        'total_amount': '0.00',
                        'customer_name': customer.company_name,
                        'start_date': start_date,
                        'end_date': end_date
                    }
                
                # Ensure orders is a list
                if 'orders' not in report_data:
                    report_data['orders'] = []
                
                # Ensure each order has required fields
                for order in report_data['orders']:
                    if 'services' not in order:
                        order['services'] = []
                    if 'total_amount' not in order:
                        order['total_amount'] = '0.00'
                    if 'date' not in order:
                        order['date'] = ''

                logger.info("Report data structured successfully")

                # Save report to database
                report = BillingReport.objects.create(
                    customer=customer,
                    start_date=start_date,
                    end_date=end_date,
                    total_amount=report_data.get('total_amount', '0.00'),
                    report_data=report_data
                )

                # Handle different output formats
                if output_format == 'excel':
                    excel_file = generate_excel_report(report_data)
                    response = HttpResponse(
                        excel_file.read(),
                        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                    )
                    response['Content-Disposition'] = 'attachment; filename="billing_report.xlsx"'
                    return response
                
                elif output_format == 'pdf':
                    pdf_file = generate_pdf_report(report_data)
                    response = HttpResponse(pdf_file.read(), content_type='application/pdf')
                    response['Content-Disposition'] = 'attachment; filename="billing_report.pdf"'
                    return response
                
                else:  # preview format
                    return Response({
                        'success': True,
                        'message': 'Report generated successfully',
                        'data': {
                            'report_id': report.id,
                            'preview_data': report_data,
                            'customer_name': customer.company_name,
                            'start_date': start_date,
                            'end_date': end_date,
                            'total_amount': str(report_data.get('total_amount', '0.00'))
                        }
                    })

            except Exception as e:
                error_msg = f"Error generating report: {str(e)}"
                logger.error(error_msg)
                return Response(
                    {"error": error_msg},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(error_msg)
            return Response(
                {"error": error_msg},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )