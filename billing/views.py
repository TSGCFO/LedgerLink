from django.views.generic import TemplateView
from django.http import JsonResponse, HttpResponse
from django.core.exceptions import ValidationError
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .forms import BillingReportForm
from .models import BillingReport, Customer
from .serializers import BillingReportSerializer, ReportRequestSerializer
from .services import BillingReportService
from .utils import ReportFileHandler
import logging
from django.utils import timezone

logger = logging.getLogger('billing')

@method_decorator([ensure_csrf_cookie, csrf_exempt], name='dispatch')
class BillingReportView(TemplateView):
    template_name = 'billing/billing_report.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = BillingReportForm()
        return context

@method_decorator(csrf_exempt, name='dispatch')
class BillingReportListView(APIView):
    serializer_class = BillingReportSerializer

    def get(self, request):
        try:
            # Get query parameters
            customer_id = request.query_params.get('customer')
            start_date = request.query_params.get('start_date')
            end_date = request.query_params.get('end_date')

            # Build the queryset with filters
            queryset = BillingReport.objects.select_related('customer')

            if customer_id:
                queryset = queryset.filter(customer_id=customer_id)
            if start_date:
                queryset = queryset.filter(start_date__gte=start_date)
            if end_date:
                queryset = queryset.filter(end_date__lte=end_date)

            serializer = self.serializer_class(queryset, many=True)
            
            return Response({
                'success': True,
                'data': serializer.data,
                'count': len(serializer.data)
            })
        except Exception as e:
            logger.error(f"Error fetching billing reports: {str(e)}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@method_decorator(csrf_exempt, name='dispatch')
class GenerateReportAPIView(APIView):
    serializer_class = ReportRequestSerializer

    def post(self, request):
        try:
            serializer = self.serializer_class(data=request.data)
            if not serializer.is_valid():
                return Response({
                    'success': False,
                    'error': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)

            service = BillingReportService()  # Removed user parameter for development
            
            result = service.generate_report(
                customer_id=serializer.validated_data['customer'],
                start_date=serializer.validated_data['start_date'],
                end_date=serializer.validated_data['end_date'],
                output_format=serializer.validated_data.get('output_format', 'preview')
            )

            output_format = serializer.validated_data.get('output_format', 'preview')
            
            if output_format == 'preview':
                customer = Customer.objects.get(id=serializer.validated_data['customer'])
                
                preview_data = {
                    'success': True,
                    'data': {
                        'customer_name': customer.company_name,
                        'start_date': serializer.validated_data['start_date'].isoformat(),
                        'end_date': serializer.validated_data['end_date'].isoformat(),
                        'preview_data': result,
                        'total_amount': str(result.get('total_amount', '0.00')),
                        'service_totals': result.get('service_totals', {}),
                        'generated_at': timezone.now().isoformat()
                    }
                }
                
                return Response(preview_data)
            else:
                content_type = ReportFileHandler.get_content_type(output_format)
                file_extension = ReportFileHandler.get_file_extension(output_format)
                
                response = HttpResponse(
                    result.getvalue(),
                    content_type=content_type
                )
                response['Content-Disposition'] = f'attachment; filename="billing_report.{file_extension}"'
                return response

        except ValidationError as e:
            logger.warning(f"Validation error: {str(e)}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Customer.DoesNotExist:
            logger.error(f"Customer not found: {serializer.validated_data.get('customer')}")
            return Response({
                'success': False,
                'error': 'Customer not found'
            }, status=status.HTTP_404_NOT_FOUND)
            
        except Exception as e:
            logger.error(f"Error generating report: {str(e)}")
            return Response({
                'success': False,
                'error': 'Failed to generate report'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)