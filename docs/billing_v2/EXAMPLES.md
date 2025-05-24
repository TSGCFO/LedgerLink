# Billing V2 Examples and Recipes

This document provides practical examples and common use cases for the Billing V2 system.

## Table of Contents

1. [Generating Reports](#generating-reports)
2. [Working with the API](#working-with-the-api)
3. [Using Management Commands](#using-management-commands)
4. [Report Analysis](#report-analysis)
5. [Integration Examples](#integration-examples)
6. [Customization](#customization)

## Generating Reports

### Generate a Report for a Customer for the Last Month

```python
from datetime import datetime, timedelta
from Billing_V2.utils.calculator import generate_billing_report

# Calculate date range for last month
today = datetime.now()
first_day_of_month = datetime(today.year, today.month, 1)
last_month_end = first_day_of_month - timedelta(days=1)
last_month_start = datetime(last_month_end.year, last_month_end.month, 1)

# Generate report
report = generate_billing_report(
    customer_id=123,
    start_date=last_month_start,
    end_date=last_month_end,
    output_format='dict'
)

print(f"Generated report for {report['customer_name']}")
print(f"Total amount: ${report['total_amount']}")
print(f"Orders: {len(report['orders'])}")
```

### Generate Reports for All Active Customers

```python
from customers.models import Customer
from Billing_V2.utils.calculator import generate_billing_report
from datetime import datetime, timedelta
import os

# Set date range
start_date = datetime(2023, 1, 1)
end_date = datetime(2023, 1, 31)

# Create output directory
output_dir = 'reports/monthly/2023-01'
os.makedirs(output_dir, exist_ok=True)

# Generate reports for all active customers
active_customers = Customer.objects.filter(is_active=True)
for customer in active_customers:
    try:
        # Generate report as CSV
        report_csv = generate_billing_report(
            customer_id=customer.id,
            start_date=start_date,
            end_date=end_date,
            output_format='csv'
        )
        
        # Save to file
        filename = f"billing_report_{customer.id}_{start_date.strftime('%Y%m%d')}.csv"
        file_path = os.path.join(output_dir, filename)
        with open(file_path, 'w') as f:
            f.write(report_csv)
            
        print(f"Generated report for {customer.company_name} saved to {file_path}")
    except Exception as e:
        print(f"Error generating report for customer {customer.company_name}: {str(e)}")
```

## Working with the API

### Generate a Report and Download as CSV

```javascript
// Frontend JavaScript example using fetch
async function generateAndDownloadReport(customerId, startDate, endDate) {
  try {
    // Generate the report
    const response = await fetch('/api/v2/reports/generate/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + localStorage.getItem('token')
      },
      body: JSON.stringify({
        customer_id: customerId,
        start_date: startDate,
        end_date: endDate,
        output_format: 'json'
      })
    });
    
    if (!response.ok) {
      throw new Error(`Error generating report: ${response.statusText}`);
    }
    
    const reportData = await response.json();
    
    // Download the report as CSV
    window.location.href = `/api/v2/reports/${reportData.id}/download/?format=csv`;
    
    return reportData;
  } catch (error) {
    console.error('Error:', error);
    throw error;
  }
}

// Usage
generateAndDownloadReport(123, '2023-01-01', '2023-01-31')
  .then(report => {
    console.log(`Generated report #${report.id} with total ${report.total_amount}`);
  })
  .catch(error => {
    alert('Error generating report: ' + error.message);
  });
```

### Fetch Customer Billing Summary

```python
import requests
import matplotlib.pyplot as plt
import numpy as np

def get_customer_billing_summary(token):
    url = 'https://example.com/api/v2/reports/customer-summary/'
    headers = {'Authorization': f'Bearer {token}'}
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    return response.json()

def visualize_customer_billing(summary_data):
    # Extract data for visualization
    customers = [item['customer_name'] for item in summary_data]
    amounts = [item['total_amount'] for item in summary_data]
    report_counts = [item['report_count'] for item in summary_data]
    
    # Sort by total amount
    sorted_indices = np.argsort(amounts)[::-1]  # Descending order
    customers = [customers[i] for i in sorted_indices]
    amounts = [amounts[i] for i in sorted_indices]
    report_counts = [report_counts[i] for i in sorted_indices]
    
    # Take top 10 customers
    customers = customers[:10]
    amounts = amounts[:10]
    report_counts = report_counts[:10]
    
    # Create figure with two subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    
    # Plot total amount by customer
    bars1 = ax1.bar(customers, amounts)
    ax1.set_title('Total Billing Amount by Customer')
    ax1.set_xlabel('Customer')
    ax1.set_ylabel('Total Amount ($)')
    ax1.tick_params(axis='x', rotation=45)
    
    # Add data labels on bars
    for bar in bars1:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                f'${height:,.2f}', ha='center', va='bottom')
    
    # Plot report count by customer
    bars2 = ax2.bar(customers, report_counts)
    ax2.set_title('Number of Billing Reports by Customer')
    ax2.set_xlabel('Customer')
    ax2.set_ylabel('Report Count')
    ax2.tick_params(axis='x', rotation=45)
    
    # Add data labels on bars
    for bar in bars2:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                f'{height}', ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig('customer_billing_summary.png')
    plt.show()

# Usage
token = 'YOUR_API_TOKEN'
summary_data = get_customer_billing_summary(token)
visualize_customer_billing(summary_data)
```

## Using Management Commands

### Scheduled Monthly Report Generation

Create a bash script for generating monthly reports:

```bash
#!/bin/bash
# monthly_reports.sh

# Set variables
MONTH=$(date -d "last month" +%Y-%m)
START_DATE="${MONTH}-01"
END_DATE=$(date -d "${START_DATE} + 1 month - 1 day" +%Y-%m-%d)
OUTPUT_DIR="/path/to/reports/${MONTH}"

# Create output directory
mkdir -p "${OUTPUT_DIR}"

# Activate virtual environment
source /path/to/venv/bin/activate

# Change to project directory
cd /path/to/project

# Generate reports for all customers
python manage.py generate_billing_report \
  --all-customers \
  --start-date="${START_DATE}" \
  --end-date="${END_DATE}" \
  --output-format=csv \
  --output-dir="${OUTPUT_DIR}"

# Export combined report for data analysis
python manage.py export_billing_reports "${OUTPUT_DIR}/combined" \
  --format=csv \
  --start-date="${START_DATE}" \
  --end-date="${END_DATE}" \
  --combine

# Log completion
echo "$(date): Generated monthly billing reports for ${MONTH}" >> /var/log/billing_reports.log
```

Make the script executable and add it to crontab to run on the 1st of each month:

```bash
chmod +x monthly_reports.sh

# Add to crontab (runs at 2 AM on the 1st of each month)
crontab -e
0 2 1 * * /path/to/monthly_reports.sh
```

### Database Maintenance Script

Create a script to clean up old reports and manage database size:

```bash
#!/bin/bash
# billing_maintenance.sh

# Set variables
LOG_FILE="/var/log/billing_maintenance.log"
EMAIL="admin@example.com"
RETENTION_DAYS=365  # Keep reports for 1 year

# Activate virtual environment
source /path/to/venv/bin/activate

# Change to project directory
cd /path/to/project

# Log start
echo "$(date): Starting billing system maintenance" >> "${LOG_FILE}"

# Export all reports to archive before deletion
ARCHIVE_DIR="/path/to/archives/$(date +%Y%m%d)"
mkdir -p "${ARCHIVE_DIR}"

echo "Exporting reports to archive..." >> "${LOG_FILE}"
python manage.py export_billing_reports "${ARCHIVE_DIR}" \
  --format=json \
  --end-date="$(date -d "${RETENTION_DAYS} days ago" +%Y-%m-%d)" \
  --combine

# Clean up old reports
echo "Cleaning up old reports..." >> "${LOG_FILE}"
python manage.py cleanup_billing_reports \
  --days="${RETENTION_DAYS}" \
  --no-input >> "${LOG_FILE}" 2>&1

# Send email notification
echo "Maintenance complete. See log at ${LOG_FILE}" | \
  mail -s "Billing System Maintenance Complete" "${EMAIL}"

echo "$(date): Maintenance completed" >> "${LOG_FILE}"
```

## Report Analysis

### Analyzing Service Costs

```python
import pandas as pd
import matplotlib.pyplot as plt
from django.db.models import Sum, Count, F
from Billing_V2.models import BillingReport, OrderCost, ServiceCost

def analyze_service_costs(start_date, end_date):
    # Get all service costs for reports in the date range
    service_costs = ServiceCost.objects.filter(
        order_cost__billing_report__start_date__gte=start_date,
        order_cost__billing_report__end_date__lte=end_date
    ).values('service_id', 'service_name').annotate(
        total_amount=Sum('amount'),
        order_count=Count('order_cost', distinct=True)
    ).order_by('-total_amount')
    
    # Convert to DataFrame for analysis
    df = pd.DataFrame(list(service_costs))
    
    # Calculate percentage of total
    total_billing = df['total_amount'].sum()
    df['percentage'] = (df['total_amount'] / total_billing * 100).round(2)
    
    # Calculate average cost per order
    df['avg_per_order'] = (df['total_amount'] / df['order_count']).round(2)
    
    # Print summary
    print(f"Service Cost Analysis ({start_date} to {end_date})")
    print(f"Total Billing: ${total_billing:,.2f}")
    print("\nTop Services by Total Amount:")
    print(df[['service_name', 'total_amount', 'percentage', 'order_count', 'avg_per_order']].head(10))
    
    # Create visualization
    plt.figure(figsize=(12, 6))
    
    # Plot only top 5 services, combine others
    top_5 = df.head(5)
    others = pd.DataFrame([{
        'service_name': 'Others',
        'total_amount': df.iloc[5:]['total_amount'].sum(),
        'percentage': df.iloc[5:]['percentage'].sum()
    }])
    plot_data = pd.concat([top_5, others])
    
    # Create pie chart
    plt.pie(
        plot_data['total_amount'],
        labels=plot_data['service_name'],
        autopct='%1.1f%%',
        startangle=90,
        shadow=True,
        explode=[0.1 if i == 0 else 0 for i in range(len(plot_data))]
    )
    plt.axis('equal')
    plt.title(f'Service Cost Distribution ({start_date} to {end_date})')
    plt.tight_layout()
    plt.savefig('service_cost_analysis.png')
    plt.show()
    
    return df

# Usage
df = analyze_service_costs('2023-01-01', '2023-12-31')
```

### Customer Billing Trends

```python
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from Billing_V2.models import BillingReport

def analyze_customer_billing_trends(customer_id, years=2):
    # Get reports for the customer over the specified years
    reports = BillingReport.objects.filter(
        customer_id=customer_id,
        created_at__gte=pd.Timestamp.now() - pd.DateOffset(years=years)
    ).annotate(
        month=TruncMonth('start_date')
    ).values('month').annotate(
        total_amount=Sum('total_amount')
    ).order_by('month')
    
    # Convert to DataFrame and set month as index
    df = pd.DataFrame(list(reports))
    if df.empty:
        print(f"No data found for customer {customer_id}")
        return None
    
    df['month'] = pd.to_datetime(df['month'])
    df.set_index('month', inplace=True)
    
    # Resample to fill in missing months with zeros
    monthly = df.resample('M').sum().fillna(0)
    
    # Add 3-month moving average
    monthly['moving_avg_3m'] = monthly['total_amount'].rolling(window=3, min_periods=1).mean()
    
    # Get customer name
    customer_name = BillingReport.objects.filter(
        customer_id=customer_id
    ).first().customer.company_name
    
    # Plotting
    plt.figure(figsize=(12, 6))
    ax = plt.gca()
    
    # Plot monthly totals as bars
    monthly['total_amount'].plot(kind='bar', ax=ax, color='skyblue', alpha=0.7)
    
    # Plot moving average as line
    monthly['moving_avg_3m'].plot(kind='line', ax=ax, color='red', linewidth=2)
    
    # Format x-axis to show month and year
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    plt.xticks(rotation=45)
    
    # Add labels and title
    plt.title(f'Monthly Billing Totals for {customer_name} (Last {years} Years)')
    plt.xlabel('Month')
    plt.ylabel('Billing Amount ($)')
    plt.legend(['3-Month Moving Average', 'Monthly Total'])
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Add data values on top of bars
    for i, v in enumerate(monthly['total_amount']):
        if v > 0:
            plt.text(i, v + 50, f'${v:,.0f}', ha='center', rotation=90, fontsize=8)
    
    plt.tight_layout()
    plt.savefig(f'customer_{customer_id}_billing_trends.png')
    plt.show()
    
    return monthly

# Usage
monthly_data = analyze_customer_billing_trends(123, years=2)
```

## Integration Examples

### Django Rest Framework Custom Action

Adding a custom action to export all reports for a customer:

```python
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse
import csv
import io
from datetime import datetime

class BillingReportViewSet(viewsets.ModelViewSet):
    # ... existing code ...
    
    @action(detail=False, methods=['get'])
    def export_customer_reports(self, request):
        """Export all reports for a customer as a single CSV file"""
        customer_id = request.query_params.get('customer_id')
        if not customer_id:
            return Response(
                {"error": "customer_id parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            # Verify customer exists
            customer = Customer.objects.get(id=customer_id)
            
            # Get all reports for the customer
            reports = BillingReport.objects.filter(customer_id=customer_id)
            if not reports.exists():
                return Response(
                    {"error": f"No reports found for customer {customer_id}"},
                    status=status.HTTP_404_NOT_FOUND
                )
                
            # Create CSV file in memory
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write header
            writer.writerow([
                'Report ID', 'Start Date', 'End Date', 'Created At',
                'Order ID', 'Reference Number', 'Order Date',
                'Service ID', 'Service Name', 'Amount'
            ])
            
            # Write rows
            for report in reports:
                report_row = [
                    report.id,
                    report.start_date.strftime('%Y-%m-%d'),
                    report.end_date.strftime('%Y-%m-%d'),
                    report.created_at.strftime('%Y-%m-%d %H:%M:%S')
                ]
                
                for order_cost in report.order_costs.all():
                    order_row = report_row + [
                        order_cost.order.transaction_id,
                        order_cost.order.reference_number,
                        order_cost.order.created_at.strftime('%Y-%m-%d')
                    ]
                    
                    for service_cost in order_cost.service_costs.all():
                        service_row = order_row + [
                            service_cost.service_id,
                            service_cost.service_name,
                            service_cost.amount
                        ]
                        writer.writerow(service_row)
            
            # Prepare response
            output.seek(0)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"customer_{customer_id}_reports_{timestamp}.csv"
            
            response = HttpResponse(output.read(), content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            
            return response
            
        except Customer.DoesNotExist:
            return Response(
                {"error": f"Customer with ID {customer_id} not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
```

### Integrating with External Systems

```python
import requests
import json
from datetime import datetime, timedelta
from django.conf import settings
from Billing_V2.utils.calculator import generate_billing_report
from customers.models import Customer

def export_to_accounting_system(customer_id, start_date, end_date):
    """
    Generate a billing report and export it to an external accounting system.
    """
    try:
        # Generate the billing report
        report_data = generate_billing_report(
            customer_id=customer_id,
            start_date=start_date,
            end_date=end_date,
            output_format='dict'
        )
        
        # Get customer details
        customer = Customer.objects.get(id=customer_id)
        
        # Transform data for accounting system
        accounting_data = {
            'client': {
                'id': customer.id,
                'name': customer.company_name,
                'email': customer.email,
                'reference': customer.external_reference
            },
            'invoice': {
                'date': datetime.now().strftime('%Y-%m-%d'),
                'due_date': (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'),
                'reference': f"INV-{report_data['id']}",
                'description': f"Billing for period {start_date} to {end_date}",
                'currency': 'USD',
                'total_amount': float(report_data['total_amount'])
            },
            'line_items': []
        }
        
        # Add line items for each service
        for service_id, service_data in report_data['service_totals'].items():
            accounting_data['line_items'].append({
                'description': service_data['service_name'],
                'quantity': 1,
                'unit_price': float(service_data['amount']),
                'amount': float(service_data['amount']),
                'tax_rate': 0.0
            })
        
        # Send to accounting API
        api_url = settings.ACCOUNTING_API_URL
        api_key = settings.ACCOUNTING_API_KEY
        
        response = requests.post(
            f"{api_url}/invoices",
            headers={
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            },
            data=json.dumps(accounting_data)
        )
        
        response.raise_for_status()
        
        # Return the response data
        return {
            'report_id': report_data['id'],
            'invoice_id': response.json().get('id'),
            'status': 'success',
            'message': 'Successfully exported to accounting system'
        }
        
    except Customer.DoesNotExist:
        return {
            'status': 'error',
            'message': f'Customer with ID {customer_id} not found'
        }
    except requests.RequestException as e:
        return {
            'status': 'error',
            'message': f'Error connecting to accounting system: {str(e)}'
        }
    except Exception as e:
        return {
            'status': 'error',
            'message': f'Unexpected error: {str(e)}'
        }

# Usage
result = export_to_accounting_system(
    customer_id=123,
    start_date='2023-01-01',
    end_date='2023-01-31'
)
print(result)
```

## Customization

### Adding a Custom Service Cost Calculator

If you need a specialized calculation method for a specific service:

```python
# In utils/calculator.py

def calculate_custom_service_cost(customer_service, order):
    """
    Custom calculation method for a specific service type.
    
    Args:
        customer_service: CustomerService object
        order: Order object
        
    Returns:
        Decimal cost amount
    """
    service = customer_service.service
    service_name = service.name.lower()
    
    # Example: Volume-based pricing with tiers
    if service_name == 'storage' and order.volume_cuft:
        volume = order.volume_cuft
        unit_price = customer_service.unit_price
        
        # Define tiers
        if volume <= 10:
            # Standard rate
            return unit_price * volume
        elif volume <= 50:
            # Discount for medium volume
            return unit_price * 10 + (unit_price * 0.8) * (volume - 10)
        else:
            # Discount for high volume
            return unit_price * 10 + (unit_price * 0.8) * 40 + (unit_price * 0.6) * (volume - 50)
    
    # Default to regular calculation
    return None

# Update the calculate_service_cost method in BillingCalculator class
def calculate_service_cost(self, customer_service, order):
    """Calculate the cost for a service applied to an order."""
    try:
        # Check for custom calculator first
        custom_cost = calculate_custom_service_cost(customer_service, order)
        if custom_cost is not None:
            return custom_cost
            
        # Continue with regular calculation...
        # ...
    except Exception as e:
        logger.error(f"Error calculating service cost: {str(e)}")
        return Decimal('0')
```

### Custom Report Format

Adding a custom report format (like PDF):

```python
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO

def generate_pdf_report(report):
    """
    Generate a PDF report for a billing report.
    
    Args:
        report: BillingReport object
        
    Returns:
        BytesIO object containing the PDF file
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    
    # Get styles
    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    subtitle_style = styles['Heading2']
    normal_style = styles['Normal']
    
    # Add title
    elements.append(Paragraph(f"Billing Report #{report.id}", title_style))
    elements.append(Spacer(1, 12))
    
    # Add customer info
    elements.append(Paragraph(f"Customer: {report.customer.company_name}", subtitle_style))
    elements.append(Paragraph(f"Period: {report.start_date.strftime('%Y-%m-%d')} to {report.end_date.strftime('%Y-%m-%d')}", normal_style))
    elements.append(Paragraph(f"Generated: {report.created_at.strftime('%Y-%m-%d %H:%M:%S')}", normal_style))
    elements.append(Spacer(1, 24))
    
    # Add service totals
    elements.append(Paragraph("Service Totals", subtitle_style))
    elements.append(Spacer(1, 12))
    
    # Create service totals table
    service_data = [['Service', 'Amount']]
    for service_id, service_info in report.service_totals.items():
        service_data.append([
            service_info['service_name'],
            f"${service_info['amount']:,.2f}"
        ])
    
    # Add total row
    service_data.append(['Total', f"${report.total_amount:,.2f}"])
    
    # Create table
    service_table = Table(service_data, colWidths=[350, 100])
    service_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BOX', (0, 0), (-1, -1), 2, colors.black),
    ]))
    
    elements.append(service_table)
    elements.append(Spacer(1, 24))
    
    # Add order details
    elements.append(Paragraph("Order Details", subtitle_style))
    elements.append(Spacer(1, 12))
    
    # Create order details table
    for order_cost in report.order_costs.all():
        order = order_cost.order
        elements.append(Paragraph(
            f"Order #{order.transaction_id} - {order.reference_number} - {order.created_at.strftime('%Y-%m-%d')}",
            styles['Heading3']
        ))
        elements.append(Spacer(1, 6))
        
        # Create services table for this order
        order_data = [['Service', 'Amount']]
        for service_cost in order_cost.service_costs.all():
            order_data.append([
                service_cost.service_name,
                f"${service_cost.amount:,.2f}"
            ])
        
        # Add total row
        order_data.append(['Total', f"${order_cost.total_amount:,.2f}"])
        
        # Create table
        order_table = Table(order_data, colWidths=[350, 100])
        order_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BOX', (0, 0), (-1, -1), 2, colors.black),
        ]))
        
        elements.append(order_table)
        elements.append(Spacer(1, 12))
    
    # Build the PDF
    doc.build(elements)
    buffer.seek(0)
    
    return buffer

# Add PDF support to BillingReportViewSet
@action(detail=True, methods=['get'])
def download(self, request, pk=None):
    """Download a billing report in specified format"""
    report = self.get_object()
    
    format_type = request.query_params.get('format', 'csv')
    
    try:
        if format_type == 'pdf':
            # Generate PDF
            pdf_buffer = generate_pdf_report(report)
            
            # Return as file download
            response = HttpResponse(pdf_buffer.read(), content_type='application/pdf')
            filename = f"billing_report_{report.id}.pdf"
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            
            return response
            
        # Other formats...
    except Exception as e:
        logger.error(f"Error downloading report: {str(e)}")
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
```
