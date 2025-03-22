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
        import time
        start_time = time.time()
        
        # Validate request data
        validation_start = time.time()
        serializer = BillingReportRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'error': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        validation_time = time.time() - validation_start
        logger.info(f"Request validation completed in {validation_time:.2f} seconds")
            
        data = serializer.validated_data
        
        # Generate report
        try:
            # Initialize calculator
            init_start = time.time()
            
            # Handle customer_services parameter explicitly
            customer_service_ids = data.get('customer_services')
            logger.info(f"Raw request data: {request.data}")
            logger.info(f"Initial customer_service_ids: {customer_service_ids} (type: {type(customer_service_ids)})")
            
            if customer_service_ids is not None:
                # Ensure it's a proper list of integers
                if isinstance(customer_service_ids, list):
                    # Already a list - convert elements to int if needed
                    original_ids = customer_service_ids.copy()
                    customer_service_ids = [int(id) for id in customer_service_ids if id]
                    logger.info(f"List format - Original: {original_ids}, Converted: {customer_service_ids}")
                elif isinstance(customer_service_ids, str):
                    # Convert string to list if needed (e.g. '1,2,3')
                    if ',' in customer_service_ids:
                        original_str = customer_service_ids
                        customer_service_ids = [int(id.strip()) for id in customer_service_ids.split(',') if id.strip()]
                        logger.info(f"String format with commas - Original: '{original_str}', Converted: {customer_service_ids}")
                    else:
                        # Single ID
                        original_str = customer_service_ids
                        customer_service_ids = [int(customer_service_ids)]
                        logger.info(f"Single ID string - Original: '{original_str}', Converted: {customer_service_ids}")
                else:
                    # Unknown format - log and use None (all services)
                    logger.warning(f"Unrecognized customer_service_ids format: {customer_service_ids}, using None (all services)")
                    customer_service_ids = None
                
                # List all CustomerService objects for this customer to help with debugging
                from customer_services.models import CustomerService
                all_services = list(CustomerService.objects.filter(customer_id=data['customer_id']).values('id', 'service__id', 'service__service_name'))
                logger.info(f"All available customer services for customer {data['customer_id']}: {all_services}")
                logger.info(f"Final customer_service_ids to be used: {customer_service_ids}")
            
            calculator = BillingCalculator(
                customer_id=data['customer_id'],
                start_date=data['start_date'],
                end_date=data['end_date'],
                customer_service_ids=customer_service_ids
            )
            init_time = time.time() - init_start
            
            # Store the calculator in request.session for progress tracking
            # We'll use a unique key based on customer and date range
            progress_key = f"billing_report_progress_{data['customer_id']}_{data['start_date']}_{data['end_date']}"
            
            # Store in Django's cache
            from django.core.cache import cache
            cache.set(progress_key, calculator.progress, 3600)  # Cache for 1 hour
            
            # Generate the report
            logger.info(f"Starting report generation for customer {data['customer_id']} from {data['start_date']} to {data['end_date']}")
            report_gen_start = time.time()
            report = calculator.generate_report()
            report_gen_time = time.time() - report_gen_start
            
            # Store the report ID in the progress data for reference
            calculator.progress['report_id'] = report.id
            cache.set(progress_key, calculator.progress, 3600)  # Update cache
            
            logger.info(f"Completed report generation: Report ID {report.id} in {report_gen_time:.2f} seconds")
            
            # Return based on requested format
            output_format = data.get('output_format', 'json')
            
            # Start formatting response
            format_start = time.time()
            
            if output_format == 'json':
                # Return report as JSON with consistent format
                report_serializer = self.get_serializer(report)
                response = Response({
                    'success': True,
                    'data': report_serializer.data,
                    'metrics': {
                        'generation_time': report_gen_time,
                        'total_time': time.time() - start_time
                    }
                }, status=status.HTTP_201_CREATED)
                
            elif output_format == 'csv':
                # Return report as CSV file
                csv_start = time.time()
                csv_content = calculator.to_csv()
                csv_time = time.time() - csv_start
                logger.info(f"CSV generation completed in {csv_time:.2f} seconds")
                
                # Get customer name for better filename
                try:
                    from customers.models import Customer
                    customer = Customer.objects.get(id=data['customer_id'])
                    customer_name = customer.company_name.replace(" ", "_")
                except Exception:
                    customer_name = f"customer_{data['customer_id']}"
                
                # Format dates for filename
                start_date_str = data['start_date'].strftime('%Y%m%d')
                end_date_str = data['end_date'].strftime('%Y%m%d')
                
                # Create response with CSV content
                response = HttpResponse(content_type='text/csv; charset=utf-8')
                filename = f"billing_report_{customer_name}_{start_date_str}_to_{end_date_str}.csv"
                
                # Use proper Content-Disposition header with quoted filename
                response['Content-Disposition'] = f'attachment; filename="{filename}"'
                # Add additional headers to prevent caching
                response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
                response['Pragma'] = 'no-cache'
                response['Expires'] = '0'
                
                # Write the CSV content to the response
                response.write(csv_content)
                
                # Log success
                logger.info(f"CSV file prepared for download: {filename} ({len(csv_content)} bytes)")
                
            elif output_format == 'pdf':
                # PDF generation would go here (requires additional libraries)
                response = Response({
                    "success": False,
                    "error": "PDF generation not implemented yet",
                    "metrics": {
                        "generation_time": report_gen_time,
                        "total_time": time.time() - start_time
                    }
                }, 
                status=status.HTTP_501_NOT_IMPLEMENTED
                )
                
            elif output_format == 'dict':
                # Return as dictionary directly (useful for internal API calls)
                response = Response({
                    "success": True,
                    "data": report.to_dict(),
                    "metrics": {
                        "generation_time": report_gen_time,
                        "total_time": time.time() - start_time
                    }
                }, status=status.HTTP_201_CREATED)
            
            else:
                response = Response({
                    "success": False,
                    "error": f"Invalid output format: {output_format}"
                },
                status=status.HTTP_400_BAD_REQUEST
                )
            
            # Log total processing time
            format_time = time.time() - format_start
            total_time = time.time() - start_time
            logger.info(f"Report response formatting completed in {format_time:.2f} seconds")
            logger.info(f"Total report generation and response time: {total_time:.2f} seconds")
            
            return response
                
        except ValidationError as e:
            logger.error(f"Validation error generating billing report: {str(e)}")
            return Response({
                "success": False,
                "error": str(e),
                "metrics": {
                    "total_time": time.time() - start_time
                }
            },
            status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error generating billing report: {str(e)}")
            return Response({
                "success": False,
                "error": "An unexpected error occurred generating the report. Please try again.",
                "metrics": {
                    "total_time": time.time() - start_time
                }
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'], url_path='download')
    def download(self, request, pk=None):
        """Download a billing report in specified format"""
        import time
        start_time = time.time()
        
        try:
            # Get the report - use get_object() which handles permissions
            report = self.get_object()
            
            # Get requested format - default to CSV
            format_type = request.query_params.get('format', 'csv')
            
            # Log download request
            logger.info(f"Download requested for report {report.id} in {format_type} format")
            
            if format_type == 'csv':
                # Initialize calculator with the existing report
                calculator = BillingCalculator(
                    customer_id=report.customer_id,
                    start_date=report.start_date,
                    end_date=report.end_date
                )
                calculator.report = report  # Set existing report
                
                # Set filename with customer name and date range for better identification
                try:
                    customer_name = report.customer.company_name.replace(" ", "_")
                except Exception:
                    customer_name = f"customer_{report.customer_id}"
                    
                start_date_str = report.start_date.strftime('%Y%m%d')
                end_date_str = report.end_date.strftime('%Y%m%d')
                filename = f"billing_report_{customer_name}_{start_date_str}_to_{end_date_str}.csv"
                
                # Generate CSV content
                csv_start = time.time()
                csv_content = calculator.to_csv()
                csv_time = time.time() - csv_start
                
                # Create response with proper headers
                response = HttpResponse(content_type='text/csv; charset=utf-8')
                response['Content-Disposition'] = f'attachment; filename="{filename}"'
                response['Content-Length'] = len(csv_content)
                response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
                response['Pragma'] = 'no-cache'
                response['Expires'] = '0'
                
                # Write CSV content to response
                response.write(csv_content)
                
                # Log the successful download
                total_time = time.time() - start_time
                logger.info(f"CSV download prepared for report {report.id}: {filename} ({len(csv_content)} bytes) in {total_time:.2f}s")
                
                return response
                
            elif format_type == 'json':
                # Return as JSON data
                serializer = self.get_serializer(report)
                return Response({
                    'success': True,
                    'data': serializer.data
                })
                
            elif format_type == 'pdf':
                # PDF generation would go here
                return Response({
                    'success': False,
                    'error': "PDF generation not implemented yet"
                }, status=status.HTTP_501_NOT_IMPLEMENTED)
                
            else:
                return Response({
                    'success': False,
                    'error': f"Invalid format: {format_type}"
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            logger.error(f"Error downloading report: {str(e)}")
            return Response({
                'success': False,
                'error': f"Error downloading report: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    @action(detail=False, methods=['get'], url_path='progress')
    def progress(self, request):
        """Get progress of report generation"""
        try:
            # Get required parameters
            customer_id = request.query_params.get('customer_id')
            start_date = request.query_params.get('start_date')
            end_date = request.query_params.get('end_date')
            
            # Validate required parameters
            if not all([customer_id, start_date, end_date]):
                return Response({
                    'success': False,
                    'error': "Missing required parameters: customer_id, start_date, end_date"
                }, status=status.HTTP_400_BAD_REQUEST)
                
            # Construct progress key
            progress_key = f"billing_report_progress_{customer_id}_{start_date}_{end_date}"
            
            # Get progress from cache
            from django.core.cache import cache
            progress = cache.get(progress_key)
            
            if not progress:
                return Response({
                    'success': False,
                    'error': "No progress information found for the given parameters"
                }, status=status.HTTP_404_NOT_FOUND)
                
            # Add the progress_key to the response
            progress['progress_key'] = progress_key
            
            return Response({
                'success': True,
                'data': progress
            })
            
        except Exception as e:
            logger.error(f"Error getting progress: {str(e)}")
            return Response({
                'success': False,
                'error': f"Error getting progress: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'], url_path='customer-services/(?P<customer_id>[^/.]+)')
    def customer_services(self, request, customer_id=None):
        """Get customer services for a specific customer"""
        try:
            # Validate customer ID
            from customers.models import Customer
            try:
                customer = Customer.objects.get(pk=customer_id)
            except Customer.DoesNotExist:
                return Response({
                    'success': False,
                    'error': f"Customer with ID {customer_id} not found"
                }, status=status.HTTP_404_NOT_FOUND)
                
            # Get all customer services with their related service
            from customer_services.models import CustomerService
            customer_services = CustomerService.objects.filter(
                customer_id=customer_id
            ).select_related('service')
            
            # Format the response
            services_data = []
            for cs in customer_services:
                services_data.append({
                    'id': cs.id,
                    'service_id': cs.service.id,
                    'service_name': cs.service.service_name,
                    'charge_type': cs.service.charge_type,
                    'unit_price': float(cs.unit_price) if cs.unit_price else 0,
                    'active': True  # Assuming all customer services are active by default
                })
            
            return Response({
                'success': True,
                'data': services_data
            })
            
        except Exception as e:
            logger.error(f"Error getting customer services: {str(e)}")
            return Response({
                'success': False,
                'error': f"Error getting customer services: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
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