import logging
from datetime import datetime
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

# Custom session authentication that doesn't enforce CSRF for development
class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        # Skip CSRF validation for API endpoints
        return
from django.http import HttpResponse
from django.core.exceptions import ValidationError
from .models import BillingReport
from .serializers import (
    BillingReportSerializer,
    BillingReportRequestSerializer,
    BillingReportSummarySerializer
)
from .utils.calculator import BillingCalculator

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
class BillingReportViewSet(viewsets.ModelViewSet):
    """ViewSet for billing reports"""
    
    queryset = BillingReport.objects.all()
    serializer_class = BillingReportSerializer
    # Temporarily disable authentication for development testing
    # permission_classes = [IsAuthenticated]
    permission_classes = []  # Allow all for development
    authentication_classes = [CsrfExemptSessionAuthentication]
    
    def list(self, request, *args, **kwargs):
        """Override list method to return consistent JSON format"""
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'success': True,
            'data': serializer.data
        })
        
    def retrieve(self, request, *args, **kwargs):
        """Override retrieve method to return consistent JSON format"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            'success': True,
            'data': serializer.data
        })
    
    def get_serializer_class(self):
        """Return appropriate serializer class based on action"""
        if self.action == 'list':
            return BillingReportSummarySerializer
        return self.serializer_class
    
    def get_queryset(self):
        """Filter queryset by optional parameters"""
        queryset = BillingReport.objects.all()
        
        # Filter by customer ID
        customer_id = self.request.query_params.get('customer_id')
        if customer_id:
            queryset = queryset.filter(customer_id=customer_id)
            
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        if start_date:
            queryset = queryset.filter(start_date__gte=start_date)
            
        end_date = self.request.query_params.get('end_date')
        if end_date:
            queryset = queryset.filter(end_date__lte=end_date)
            
        # Filter by created date
        created_after = self.request.query_params.get('created_after')
        if created_after:
            queryset = queryset.filter(created_at__gte=created_after)
            
        created_before = self.request.query_params.get('created_before')
        if created_before:
            queryset = queryset.filter(created_at__lte=created_before)
            
        # Order by
        order_by = self.request.query_params.get('order_by', '-created_at')
        allowed_fields = ['created_at', '-created_at', 'customer_id', '-customer_id', 
                         'start_date', '-start_date', 'end_date', '-end_date', 
                         'total_amount', '-total_amount']
        
        if order_by in allowed_fields:
            queryset = queryset.order_by(order_by)
            
        return queryset
    
    @method_decorator(csrf_exempt)
    @action(detail=False, methods=['post'])
    def generate(self, request):
        """Generate a new billing report"""
        # Validate request data
        serializer = BillingReportRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'error': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
        data = serializer.validated_data
        
        # Generate report
        try:
            calculator = BillingCalculator(
                customer_id=data['customer_id'],
                start_date=data['start_date'],
                end_date=data['end_date']
            )
            
            # Generate the report
            logger.info(f"Starting report generation for customer {data['customer_id']}")
            report = calculator.generate_report()
            logger.info(f"Completed report generation: Report ID {report.id}")
            
            # Return based on requested format
            output_format = data.get('output_format', 'json')
            
            if output_format == 'json':
                # Return report as JSON with consistent format
                report_serializer = self.get_serializer(report)
                return Response({
                    'success': True,
                    'data': report_serializer.data
                }, status=status.HTTP_201_CREATED)
                
            elif output_format == 'csv':
                # Return report as CSV file
                response = HttpResponse(content_type='text/csv')
                filename = f"billing_report_{data['customer_id']}_{data['start_date']}.csv"
                response['Content-Disposition'] = f'attachment; filename="{filename}"'
                response.write(calculator.to_csv())
                return response
                
            elif output_format == 'pdf':
                # PDF generation would go here (requires additional libraries)
                return Response({
                    "success": False,
                    "error": "PDF generation not implemented yet"
                }, 
                status=status.HTTP_501_NOT_IMPLEMENTED
                )
                
            elif output_format == 'dict':
                # Return as dictionary directly (useful for internal API calls)
                return Response({
                    "success": True,
                    "data": report.to_dict()
                }, status=status.HTTP_201_CREATED)
            
            else:
                return Response({
                    "success": False,
                    "error": f"Invalid output format: {output_format}"
                },
                status=status.HTTP_400_BAD_REQUEST
                )
                
        except ValidationError as e:
            logger.error(f"Validation error generating billing report: {str(e)}")
            return Response({
                "success": False,
                "error": str(e)
            },
            status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error generating billing report: {str(e)}")
            return Response({
                "success": False,
                "error": "An unexpected error occurred generating the report. Please try again."
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'], url_path='download')
    def download(self, request, pk=None):
        """Download a billing report in specified format"""
        report = self.get_object()
        
        format_type = request.query_params.get('format', 'csv')
        
        try:
            if format_type == 'csv':
                # Return report as CSV file
                calculator = BillingCalculator(
                    customer_id=report.customer_id,
                    start_date=report.start_date,
                    end_date=report.end_date
                )
                calculator.report = report  # Set existing report
                
                # Create response with CSV content type
                response = HttpResponse(content_type='text/csv; charset=utf-8')
                
                # Set filename with customer name and date range for better identification
                customer_name = report.customer.company_name.replace(" ", "_")
                start_date_str = report.start_date.strftime('%Y%m%d')
                end_date_str = report.end_date.strftime('%Y%m%d')
                filename = f"billing_report_{customer_name}_{start_date_str}_to_{end_date_str}.csv"
                
                # Set headers for file download
                response['Content-Disposition'] = f'attachment; filename="{filename}"'
                
                # Generate CSV content
                csv_content = calculator.to_csv()
                response.write(csv_content)
                
                # Log the successful download
                logger.info(f"Generated CSV download for report {report.id} ({len(csv_content)} bytes)")
                
                return response
                
            elif format_type == 'json':
                # Return as JSON data
                serializer = self.get_serializer(report)
                return Response(serializer.data)
                
            elif format_type == 'pdf':
                # PDF generation would go here
                return Response(
                    {"error": "PDF generation not implemented yet"}, 
                    status=status.HTTP_501_NOT_IMPLEMENTED
                )
                
            else:
                return Response(
                    {"error": f"Invalid format: {format_type}"},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except Exception as e:
            logger.error(f"Error downloading report: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
    @action(detail=False, methods=['get'])
    def customer_summary(self, request):
        """Get summary of billing reports by customer"""
        from django.db.models import Sum, Count
        from django.db import models
        
        try:
            # Get customer ID filter
            customer_id = request.query_params.get('customer_id')
            
            # Base queryset with grouping by customer
            queryset = BillingReport.objects.values('customer_id')
            
            # Apply customer filter if provided
            if customer_id:
                queryset = queryset.filter(customer_id=customer_id)
                
            # Annotate with aggregates
            summary = queryset.annotate(
                report_count=Count('id'),
                total_amount=Sum('total_amount'),
                first_report=models.Min('created_at'),
                latest_report=models.Max('created_at'),
            ).order_by('-latest_report')
            
            # Get customer names
            from customers.models import Customer
            customer_map = {
                c.id: c.company_name for c in Customer.objects.filter(
                    id__in=[item['customer_id'] for item in summary]
                )
            }
            
            # Add customer names to results
            for item in summary:
                item['customer_name'] = customer_map.get(item['customer_id'], 'Unknown')
                
            return Response(summary)
            
        except Exception as e:
            logger.error(f"Error getting customer summary: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )