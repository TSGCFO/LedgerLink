from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import BillingReport
from .utils import ReportDataValidator, ReportCache, ReportFileHandler, log_report_generation
from .billing_calculator import generate_billing_report
import logging

logger = logging.getLogger('billing')

class BillingReportService:
    """Service class for handling billing report operations"""

    def __init__(self, user=None):
        self.user = user  # User can be None in development

    @log_report_generation
    def generate_report(self, customer_id, start_date, end_date, output_format='preview'):
        """Generate a billing report"""
        try:
            # Check cache first for preview format
            if output_format == 'preview':
                cached_report = ReportCache.get_cached_report(
                    customer_id, start_date, end_date, output_format
                )
                if cached_report:
                    logger.info(f"Returning cached report for customer {customer_id}")
                    return cached_report

            # Generate report data
            report_data = self._generate_report_data(customer_id, start_date, end_date)
            
            # Validate report data
            ReportDataValidator.validate_report_data(report_data)
            
            # Check file size for non-preview formats
            if output_format != 'preview':
                estimated_size = ReportFileHandler.estimate_file_size(report_data)
                ReportFileHandler.validate_file_size(estimated_size)

            # Save report (skip in development if no user)
            if self.user:
                self._save_report(customer_id, start_date, end_date, report_data)

            # Generate output based on format
            result = None
            if output_format == 'preview':
                result = self._generate_preview(report_data)
                # Cache the preview result
                ReportCache.cache_report(
                    customer_id, start_date, end_date, result, output_format
                )
            elif output_format == 'excel':
                result = self._generate_excel(report_data)
            elif output_format == 'pdf':
                result = self._generate_pdf(report_data)
            elif output_format == 'csv':
                result = self._generate_csv(report_data)
            else:
                raise ValidationError(f"Unsupported output format: {output_format}")

            return result

        except Exception as e:
            logger.error(f"Error generating report: {str(e)}")
            raise

    @transaction.atomic
    def _save_report(self, customer_id, start_date, end_date, report_data):
        """Save the report to the database"""
        try:
            # Skip saving if no user (development mode)
            if not self.user:
                logger.info("Skipping report save in development mode")
                return None

            report = BillingReport.objects.create(
                customer_id=customer_id,
                start_date=start_date,
                end_date=end_date,
                total_amount=report_data['total_amount'],
                report_data=report_data,
                created_by=self.user,
                updated_by=self.user
            )
            logger.info(f"Saved report {report.pk} for customer {customer_id}")
            return report
        except Exception as e:
            logger.error(f"Error saving report: {str(e)}")
            raise

    def _generate_report_data(self, customer_id, start_date, end_date):
        """Generate the raw report data"""
        try:
            report_data = generate_billing_report(
                customer_id=customer_id,
                start_date=start_date,
                end_date=end_date
            )
            logger.info(f"Generated report data for customer {customer_id}")
            return report_data
        except Exception as e:
            logger.error(f"Error generating report data: {str(e)}")
            raise

    def _generate_preview(self, report_data):
        """Generate preview format of the report"""
        try:
            orders_data = report_data.get('orders', [])
            service_totals = {}

            # Calculate service totals
            for order in orders_data:
                for service in order.get('services', []):
                    service_id = service['service_id']
                    if service_id not in service_totals:
                        service_totals[service_id] = {
                            'name': service['service_name'],
                            'amount': 0,
                            'order_count': 0
                        }
                    service_totals[service_id]['amount'] += float(service['amount'])
                    service_totals[service_id]['order_count'] += 1

            preview = {
                'orders': orders_data,
                'service_totals': service_totals,
                'total_amount': str(report_data.get('total_amount', '0.00')),
                'metadata': {
                    'generated_at': timezone.now().isoformat(),
                    'record_count': len(orders_data)
                }
            }
            
            logger.info(f"Generated preview with {len(orders_data)} orders")
            return preview
            
        except Exception as e:
            logger.error(f"Error generating preview: {str(e)}")
            raise

    def _generate_excel(self, report_data):
        """Generate Excel format of the report"""
        try:
            from .exporters import generate_excel_report
            return generate_excel_report(report_data)
        except Exception as e:
            logger.error(f"Error generating Excel report: {str(e)}")
            raise

    def _generate_pdf(self, report_data):
        """Generate PDF format of the report"""
        try:
            from .exporters import generate_pdf_report
            return generate_pdf_report(report_data)
        except Exception as e:
            logger.error(f"Error generating PDF report: {str(e)}")
            raise

    def _generate_csv(self, report_data):
        """Generate CSV format of the report"""
        try:
            from .exporters import generate_csv_report
            return generate_csv_report(report_data)
        except Exception as e:
            logger.error(f"Error generating CSV report: {str(e)}")
            raise 