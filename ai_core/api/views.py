# ai_core/api/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ValidationError
from ..models import FeatureRequest, AIOperation
from ..system import AISystem
from .serializers import (
    FeatureRequestSerializer,
    AIOperationSerializer,
    CodeAnalysisSerializer,
    ImplementationStatusSerializer,
)


class AISystemViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'])
    def analyze_code(self, request):
        """
        Analyzes provided code or project structure.
        """
        serializer = CodeAnalysisSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            analyzer = AISystem.get_component('project_analyzer')
            result = analyzer.analyze_code(
                code=serializer.validated_data['code'],
                analysis_type=serializer.validated_data['analysis_type']
            )
            return Response(result)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class FeatureRequestViewSet(viewsets.ModelViewSet):
    serializer_class = FeatureRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return FeatureRequest.objects.filter(
            requested_by=self.request.user
        ).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(requested_by=self.request.user)


class AIOperationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AIOperationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return AIOperation.objects.all().order_by('-started_at')


class FeatureImplementationViewSet(viewsets.ViewSet):
    """
    ViewSet for managing feature implementations.
    """
    permission_classes = [IsAuthenticated]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.feature_manager = FeatureManager()
        self.scheduler = FeatureScheduler(self.feature_manager)
        self.monitor = ImplementationMonitor()

    @action(detail=False, methods=['post'])
    def create_request(self, request):
        """Creates a new feature request"""
        serializer = FeatureRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            feature_request = self.feature_manager.create_feature_request(
                title=serializer.validated_data['title'],
                description=serializer.validated_data['description'],
                user=request.user
            )
            return Response(
                FeatureRequestSerializer(feature_request).data,
                status=status.HTTP_201_CREATED
            )
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def implement(self, request, pk=None):
        """Starts or schedules feature implementation"""
        try:
            result = self.scheduler.schedule_implementation(
                feature_request_id=pk,
                priority=request.data.get('priority', 'normal')
            )
            return Response(result)
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['get'])
    def status(self, request, pk=None):
        """Gets implementation status"""
        try:
            status = self.feature_manager.get_implementation_status(pk)
            return Response(ImplementationStatusSerializer(status).data)
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancels an ongoing implementation"""
        try:
            result = self.feature_manager.cancel_implementation(pk)
            return Response(result)
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Gets implementation statistics"""
        stats = self.monitor.get_implementation_stats()
        return Response(stats)

    @action(detail=False, methods=['get'])
    def active(self, request):
        """Gets active implementations"""
        implementations = self.monitor.get_active_implementations()
        return Response(implementations)

    @action(detail=False, methods=['get'])
    def failed(self, request):
        """Gets failed implementations"""
        days = request.query_params.get('days', 7)
        try:
            days = int(days)
            implementations = self.monitor.get_failed_implementations(days)
            return Response(implementations)
        except ValueError:
            return Response(
                {'error': 'Invalid days parameter'},
                status=status.HTTP_400_BAD_REQUEST
            )