# rules/views.py

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.translation import gettext_lazy as _

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

import json
import logging

from products.models import Product
from .models import RuleGroup, Rule, AdvancedRule
from .forms import RuleGroupForm, RuleForm, AdvancedRuleForm
from customer_services.models import CustomerService

logger = logging.getLogger(__name__)

# API endpoints for rule group operations
@api_view(['DELETE'])
@permission_classes([AllowAny])
def delete_rule_group(request, pk):
    """Delete a rule group via API"""
    try:
        rule_group = get_object_or_404(RuleGroup, id=pk)
        
        # Log deletion attempt
        logger.info(f"Attempting to delete rule group {pk}")
        
        # Perform deletion
        rule_group.delete()
        
        # Log successful deletion
        logger.info(f"Rule group {pk} deleted successfully")
        
        return Response({
            'success': True,
            'message': 'Rule group deleted successfully'
        })
        
    except RuleGroup.DoesNotExist:
        logger.error(f"Rule group {pk} not found")
        return Response(
            {'error': 'Rule group not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Error deleting rule group {pk}: {str(e)}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# Add new API endpoint for rule deletion
@api_view(['DELETE'])
@permission_classes([AllowAny])
def delete_rule(request, pk):
    """Delete a rule via API"""
    try:
        rule = get_object_or_404(Rule, id=pk)
        group_id = rule.rule_group.id
        
        # Check for advanced rule
        is_advanced = hasattr(rule, 'advancedrule')
        
        # Log deletion attempt
        logger.info(f"Attempting to delete {'advanced ' if is_advanced else ''}rule {pk}", extra={
            'rule_id': pk,
            'group_id': group_id,
            'is_advanced': is_advanced
        })
        
        # Perform deletion
        rule.delete()
        
        # Log successful deletion
        logger.info(f"{'Advanced r' if is_advanced else 'R'}ule {pk} deleted successfully")
        
        return Response({
            'success': True,
            'message': f"{'Advanced r' if is_advanced else 'R'}ule deleted successfully",
            'group_id': group_id
        })
        
    except Rule.DoesNotExist:
        logger.error(f"Rule {pk} not found")
        return Response(
            {'error': 'Rule not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Error deleting rule {pk}: {str(e)}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import ensure_csrf_cookie
from django.http import JsonResponse
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

# New API endpoint for creating rules
@api_view(['POST', 'PUT'])
@permission_classes([AllowAny])
def create_or_update_rule(request, group_id=None, pk=None):
    """Create or update a rule via API"""
    try:
        if request.method == 'PUT':
            # Update existing rule
            rule = get_object_or_404(Rule, id=pk)
            rule.field = request.data.get('field', rule.field)
            rule.operator = request.data.get('operator', rule.operator)
            rule.value = request.data.get('value', rule.value)
            rule.adjustment_amount = request.data.get('adjustment_amount', rule.adjustment_amount)
            rule.save()
            
            logger.info(f"Rule {pk} updated successfully", extra={
                'rule_id': pk,
                'field': rule.field,
                'operator': rule.operator,
                'value': rule.value
            })
            
            return Response({
                'id': rule.id,
                'field': rule.field,
                'operator': rule.operator,
                'value': rule.value,
                'adjustment_amount': str(rule.adjustment_amount) if rule.adjustment_amount else None,
            })
        else:
            # Create new rule
            rule_group = get_object_or_404(RuleGroup, id=group_id)
            rule = Rule.objects.create(
                rule_group=rule_group,
                field=request.data.get('field'),
                operator=request.data.get('operator'),
                value=request.data.get('value'),
                adjustment_amount=request.data.get('adjustment_amount')
            )
            
            logger.info(f"New rule created for group {group_id}", extra={
                'group_id': group_id,
                'rule_id': rule.id,
                'field': rule.field,
                'operator': rule.operator,
                'value': rule.value
            })
            
            return Response({
                'id': rule.id,
                'field': rule.field,
                'operator': rule.operator,
                'value': rule.value,
                'adjustment_amount': str(rule.adjustment_amount) if rule.adjustment_amount else None,
            }, status=status.HTTP_201_CREATED)
    
    except ValidationError as e:
        logger.error(f"Validation error: {str(e)}", extra={
            'data': request.data,
            'error': str(e)
        })
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        logger.error(f"Error processing rule: {str(e)}", extra={
            'method': request.method,
            'data': request.data,
            'error': str(e)
        })
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# API Views
@method_decorator([csrf_exempt, ensure_csrf_cookie], name='dispatch')
class RuleGroupAPIView(APIView):
    permission_classes = [AllowAny]
    http_method_names = ['get', 'post', 'put', 'delete', 'options']

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        return response

    def options(self, request, *args, **kwargs):
        return Response(status=status.HTTP_200_OK)

    def get(self, request, *args, **kwargs):
        try:
            rule_groups = RuleGroup.objects.select_related(
                'customer_service',
                'customer_service__customer',
                'customer_service__service'
            ).all()
            
            data = [{
                'id': group.id,
                'customer_service': {
                    'id': group.customer_service_id,
                    'name': str(group.customer_service),
                    'customer': {
                        'id': group.customer_service.customer.id,
                        'name': group.customer_service.customer.company_name
                    },
                    'service': {
                        'id': group.customer_service.service.id,
                        'name': group.customer_service.service.service_name
                    }
                },
                'logic_operator': group.logic_operator,
                'rules': [{
                    'id': rule.id,
                    'field': rule.field,
                    'operator': rule.operator,
                    'value': rule.value,
                    'adjustment_amount': str(rule.adjustment_amount) if rule.adjustment_amount else None,
                    'advancedrule': hasattr(rule, 'advancedrule'),
                    'conditions': rule.advancedrule.conditions if hasattr(rule, 'advancedrule') else None,
                    'calculations': rule.advancedrule.calculations if hasattr(rule, 'advancedrule') else None,
                } for rule in group.rules.all()]
            } for group in rule_groups]
            
            return Response(data)
        except Exception as e:
            logger.error(f"Error fetching rule groups: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def post(self, request, *args, **kwargs):
        try:
            customer_service_id = request.data.get('customer_service')
            logic_operator = request.data.get('logic_operator', 'AND')

            if not customer_service_id:
                return Response(
                    {'error': 'Customer service is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if logic_operator not in dict(RuleGroup.LOGIC_CHOICES):
                return Response(
                    {'error': 'Invalid logic operator'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            customer_service = get_object_or_404(CustomerService, id=customer_service_id)
            
            rule_group = RuleGroup.objects.create(
                customer_service=customer_service,
                logic_operator=logic_operator
            )
            
            return Response({
                'id': rule_group.id,
                'customer_service': {
                    'id': rule_group.customer_service_id,
                    'name': str(rule_group.customer_service),
                    'customer': {
                        'id': rule_group.customer_service.customer.id,
                        'name': rule_group.customer_service.customer.company_name
                    },
                    'service': {
                        'id': rule_group.customer_service.service.id,
                        'name': rule_group.customer_service.service.service_name
                    }
                },
                'logic_operator': rule_group.logic_operator,
                'rules': []
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Error creating rule group: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

@api_view(['GET'])
@permission_classes([AllowAny])
def get_rules(request, group_id):
    """Get all basic rules for a rule group"""
    try:
        rule_group = get_object_or_404(RuleGroup, id=group_id)
        rules = rule_group.rules.filter(advancedrule=None)
        data = [{
            'id': rule.id,
            'field': rule.field,
            'operator': rule.operator,
            'value': rule.value,
            'adjustment_amount': str(rule.adjustment_amount) if rule.adjustment_amount else None,
        } for rule in rules]
        return Response(data)
    except Exception as e:
        logger.error(f"Error fetching rules: {str(e)}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([AllowAny])
def get_advanced_rules(request, group_id):
    """Get all advanced rules for a rule group"""
    try:
        rule_group = get_object_or_404(RuleGroup, id=group_id)
        rules = rule_group.rules.filter(advancedrule__isnull=False)
        data = [{
            'id': rule.id,
            'field': rule.field,
            'operator': rule.operator,
            'value': rule.value,
            'adjustment_amount': str(rule.adjustment_amount) if rule.adjustment_amount else None,
            'conditions': rule.advancedrule.conditions,
            'calculations': rule.advancedrule.calculations,
        } for rule in rules]
        return Response(data)
    except Exception as e:
        logger.error(f"Error fetching advanced rules: {str(e)}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    def get(self, request):
        """List all rule groups"""
        try:
            rule_groups = RuleGroup.objects.select_related(
                'customer_service',
                'customer_service__customer',
                'customer_service__service'
            ).all()
            
            data = [{
                'id': group.id,
                'customer_service': {
                    'id': group.customer_service_id,
                    'name': str(group.customer_service),
                    'customer': {
                        'id': group.customer_service.customer.id,
                        'name': group.customer_service.customer.company_name
                    },
                    'service': {
                        'id': group.customer_service.service.id,
                        'name': group.customer_service.service.service_name
                    }
                },
                'logic_operator': group.logic_operator,
                'rules': [{
                    'id': rule.id,
                    'field': rule.field,
                    'operator': rule.operator,
                    'value': rule.value,
                    'adjustment_amount': str(rule.adjustment_amount) if rule.adjustment_amount else None,
                    'advancedrule': hasattr(rule, 'advancedrule'),
                    'conditions': rule.advancedrule.conditions if hasattr(rule, 'advancedrule') else None,
                    'calculations': rule.advancedrule.calculations if hasattr(rule, 'advancedrule') else None,
                } for rule in group.rules.all()]
            } for group in rule_groups]
            
            return Response(data)
        except Exception as e:
            logger.error(f"Error fetching rule groups: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def post(self, request):
        """Create a new rule group"""
        try:
            customer_service_id = request.data.get('customer_service')
            logic_operator = request.data.get('logic_operator', 'AND')

            if not customer_service_id:
                return Response(
                    {'error': 'Customer service is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if logic_operator not in dict(RuleGroup.LOGIC_CHOICES):
                return Response(
                    {'error': 'Invalid logic operator'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            customer_service = get_object_or_404(CustomerService, id=customer_service_id)
            
            rule_group = RuleGroup.objects.create(
                customer_service=customer_service,
                logic_operator=logic_operator
            )
            
            return Response({
                'id': rule_group.id,
                'customer_service': {
                    'id': rule_group.customer_service_id,
                    'name': str(rule_group.customer_service),
                    'customer': {
                        'id': rule_group.customer_service.customer.id,
                        'name': rule_group.customer_service.customer.company_name
                    },
                    'service': {
                        'id': rule_group.customer_service.service.id,
                        'name': rule_group.customer_service.service.service_name
                    }
                },
                'logic_operator': rule_group.logic_operator,
                'rules': []
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Error creating rule group: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

# Rule Group Views
class RuleGroupListView(LoginRequiredMixin, ListView):
    model = RuleGroup
    template_name = 'rules/rule_group_list.html'
    context_object_name = 'rule_groups'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('q')
        customer_service = self.request.GET.get('customer_service')

        if search_query:
            queryset = queryset.filter(
                Q(customer_service__customer__company_name__icontains=search_query) |
                Q(customer_service__service__service_name__icontains=search_query)
            )

        if customer_service:
            queryset = queryset.filter(customer_service_id=customer_service)

        return queryset.select_related('customer_service',
                                     'customer_service__customer',
                                     'customer_service__service')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['customer_services'] = CustomerService.objects.all()
        return context

class RuleGroupDetailView(LoginRequiredMixin, DetailView):
    model = RuleGroup
    template_name = 'rules/rule_group_detail.html'
    context_object_name = 'rule_group'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['basic_rules'] = self.object.rules.filter(advancedrule=None)
        context['advanced_rules'] = self.object.rules.filter(advancedrule__isnull=False)
        return context

class RuleGroupCreateView(LoginRequiredMixin, CreateView):
    model = RuleGroup
    form_class = RuleGroupForm
    template_name = 'rules/rule_group_form.html'

    def get_success_url(self):
        return reverse('rules:rule_group_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Rule group created successfully.')
        return response

class RuleGroupUpdateView(LoginRequiredMixin, UpdateView):
    model = RuleGroup
    form_class = RuleGroupForm
    template_name = 'rules/rule_group_form.html'

    def get_success_url(self):
        return reverse('rules:rule_group_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Rule group updated successfully.')
        return response

class RuleGroupDeleteView(LoginRequiredMixin, DeleteView):
    model = RuleGroup
    success_url = reverse_lazy('rules:rule_group_list')

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        messages.success(request, 'Rule group deleted successfully.')
        return response

# Basic Rule Views
class RuleCreateView(LoginRequiredMixin, CreateView):
    model = Rule
    form_class = RuleForm
    template_name = 'rules/rule_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['group'] = get_object_or_404(RuleGroup, pk=self.kwargs['group_id'])
        return context

    def form_valid(self, form):
        form.instance.rule_group_id = self.kwargs['group_id']
        response = super().form_valid(form)
        messages.success(self.request, 'Rule created successfully.')
        return response

    def get_success_url(self):
        return reverse('rules:rule_group_detail',
                      kwargs={'pk': self.kwargs['group_id']})

class RuleUpdateView(LoginRequiredMixin, UpdateView):
    model = Rule
    form_class = RuleForm
    template_name = 'rules/rule_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['group'] = self.object.rule_group
        context['groupId'] = self.object.rule_group.id  # Add this line
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Rule updated successfully.')
        return response

    def get_success_url(self):
        return reverse('rules:rule_group_detail',
                      kwargs={'pk': self.object.rule_group.pk})

class RuleDeleteView(LoginRequiredMixin, DeleteView):
    model = Rule
    template_name = 'rules/rule_confirm_delete.html'

    def get_success_url(self):
        return reverse('rules:rule_group_detail',
                      kwargs={'pk': self.object.rule_group.pk})

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        messages.success(request, 'Rule deleted successfully.')
        return response

# Advanced Rule Views
class AdvancedRuleCreateView(LoginRequiredMixin, CreateView):
    model = AdvancedRule
    form_class = AdvancedRuleForm
    template_name = 'rules/advanced_rule_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['group'] = get_object_or_404(RuleGroup, pk=self.kwargs['group_id'])
        context['groupId'] = self.kwargs['group_id']  # Add this line
        context['calculation_types'] = AdvancedRule.CALCULATION_TYPES
        return context

    def form_valid(self, form):
        form.instance.rule_group_id = self.kwargs['group_id']
        try:
            response = super().form_valid(form)
            messages.success(self.request, 'Advanced rule created successfully.')
            return response
        except ValidationError as e:
            form.add_error(None, e)
            return self.form_invalid(form)

    def get_success_url(self):
        return reverse('rules:rule_group_detail',
                      kwargs={'pk': self.kwargs['group_id']})

class AdvancedRuleUpdateView(LoginRequiredMixin, UpdateView):
    model = AdvancedRule
    form_class = AdvancedRuleForm
    template_name = 'rules/advanced_rule_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['group'] = self.object.rule_group
        context['groupId'] = self.object.rule_group.id  # Add this line
        context['calculation_types'] = AdvancedRule.CALCULATION_TYPES
        return context

    def form_valid(self, form):
        try:
            response = super().form_valid(form)
            messages.success(self.request, 'Advanced rule updated successfully.')
            return response
        except ValidationError as e:
            form.add_error(None, e)
            return self.form_invalid(form)

    def get_success_url(self):
        return reverse('rules:rule_group_detail',
                      kwargs={'pk': self.object.rule_group.pk})

class AdvancedRuleDeleteView(LoginRequiredMixin, DeleteView):
    model = AdvancedRule
    template_name = 'rules/advanced_rule_confirm_delete.html'

    def get_success_url(self):
        return reverse('rules:rule_group_detail',
                      kwargs={'pk': self.object.rule_group.pk})

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        messages.success(request, 'Advanced rule deleted successfully.')
        return response

# API Views
@api_view(['GET'])
def get_operator_choices(request):
    """Return valid operators for a given field type"""
    field = request.GET.get('field')
    if not field:
        return Response(
            {'error': 'Field parameter is required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    numeric_fields = ['weight_lb', 'line_items', 'total_item_qty', 'volume_cuft', 'packages']
    string_fields = ['reference_number', 'ship_to_name', 'ship_to_company',
                    'ship_to_city', 'ship_to_state', 'ship_to_country',
                    'carrier', 'notes']
    json_fields = ['sku_quantity']

    if field in numeric_fields:
        valid_operators = ['gt', 'lt', 'eq', 'ne', 'ge', 'le']
    elif field in string_fields:
        valid_operators = ['eq', 'ne', 'contains', 'ncontains', 'startswith', 'endswith']
    elif field in json_fields:
        valid_operators = ['contains', 'ncontains']
    else:
        valid_operators = [op[0] for op in Rule.OPERATOR_CHOICES]

    operators = [
        {'value': op[0], 'label': op[1]}
        for op in Rule.OPERATOR_CHOICES
        if op[0] in valid_operators
    ]

    return Response({'operators': operators})

@api_view(['POST'])
def validate_conditions(request):
    """Validate conditions JSON structure"""
    try:
        conditions = request.data.get('conditions')
        if not conditions:
            return Response(
                {'error': 'Conditions are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create temporary advanced rule for validation
        rule = AdvancedRule(conditions=conditions)
        rule.clean()
        return Response({'valid': True})
    except ValidationError as e:
        return Response({'valid': False, 'errors': e.messages},
                       status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'error': str(e)},
                       status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def validate_calculations(request):
    """Validate calculations JSON structure"""
    try:
        calculations = request.data.get('calculations')
        if not calculations:
            return Response(
                {'error': 'Calculations are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create temporary advanced rule for validation
        rule = AdvancedRule(calculations=calculations)
        rule.clean()
        return Response({'valid': True})
    except ValidationError as e:
        return Response({'valid': False, 'errors': e.messages},
                       status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'error': str(e)},
                       status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_conditions_schema(request):
    """Return JSON schema for conditions"""
    schema = {
        "type": "object",
        "properties": {
            "field_name": {
                "type": "object",
                "properties": {
                    "operator": {"type": "string"},
                    "value": {"type": ["string", "number", "boolean"]}
                },
                "required": ["operator", "value"]
            }
        },
        "additionalProperties": True
    }
    return Response(schema)

@api_view(['GET'])
def get_calculations_schema(request):
    """Return JSON schema for calculations"""
    schema = {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "type": {
                    "type": "string",
                    "enum": AdvancedRule.CALCULATION_TYPES
                },
                "value": {"type": "number"}
            },
            "required": ["type", "value"]
        }
    }
    return Response(schema)

@api_view(['GET'])
def get_available_fields(request):
    """Return available fields and their types"""
    fields = {field[0]: {
        'label': field[1],
        'type': 'numeric' if field[0] in ['weight_lb', 'line_items', 'total_item_qty',
                                        'volume_cuft', 'packages']
        else 'json' if field[0] == 'sku_quantity'
        else 'string'
    } for field in Rule.FIELD_CHOICES}
    return Response(fields)

@api_view(['GET'])
def get_calculation_types(request):
    """Return available calculation types and their descriptions"""
    types = {
        'flat_fee': 'Add a fixed amount',
        'percentage': 'Add a percentage of the base price',
        'per_unit': 'Multiply by quantity',
        'weight_based': 'Multiply by weight',
        'volume_based': 'Multiply by volume',
        'tiered_percentage': 'Apply percentage based on value tiers',
        'product_specific': 'Apply specific rates per product'
    }
    return Response(types)

@api_view(['POST'])
def validate_rule_value(request):
    """Validate a rule value based on field type and operator"""
    try:
        field = request.data.get('field')
        operator = request.data.get('operator')
        value = request.data.get('value')

        if not all([field, operator, value]):
            return Response(
                {'error': _('Field, operator, and value are required')},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create temporary rule for validation
        rule = Rule(field=field, operator=operator, value=value)

        try:
            rule.clean()  # This will run the model's validation
            return Response({'valid': True})

        except ValidationError as e:
            return Response(
                {
                    'valid': False,
                    'errors': [str(error) for error in e.messages]
                },
                status=status.HTTP_400_BAD_REQUEST
            )

    except Exception as e:
        logger.error(f"Error validating rule value: {str(e)}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
def get_customer_skus(request, group_id):
    """Return SKUs for a specific rule group's customer"""
    try:
        rule_group = get_object_or_404(RuleGroup, id=group_id)
        customer = rule_group.customer_service.customer
        skus = Product.objects.filter(
            customer=customer
        ).values(
            'id',
            'sku',
            'labeling_unit_1',
            'labeling_quantity_1',
            'labeling_unit_2',
            'labeling_quantity_2'
        ).order_by('sku')

        return Response({
            'skus': list(skus),
            'customer': {
                'id': customer.id,
                'name': customer.company_name
            }
        })
    except Exception as e:
        logger.error(f"Error fetching SKUs: {str(e)}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )