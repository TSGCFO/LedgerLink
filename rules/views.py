from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.db.models import Q
from django.http import JsonResponse

from .models import RuleGroup, Rule
from .forms import RuleGroupForm, RuleForm
from customer_services.models import CustomerService

class RuleGroupListView(LoginRequiredMixin, ListView):
    model = RuleGroup
    template_name = 'rules/rule_group_list.html'
    context_object_name = 'rule_groups'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('q')
        customer_service = self.request.GET.get('customer_service')

        # Apply search filter
        if search_query:
            queryset = queryset.filter(
                Q(customer_service__name__icontains=search_query) |
                Q(logic_operator__icontains=search_query)
            )

        # Apply customer service filter
        if customer_service:
            queryset = queryset.filter(customer_service_id=customer_service)

        # Apply sorting
        sort_field = self.request.GET.get('sort', '-id')
        sort_direction = self.request.GET.get('direction', 'desc')

        if sort_direction == 'desc' and not sort_field.startswith('-'):
            sort_field = f'-{sort_field}'
        elif sort_direction == 'asc' and sort_field.startswith('-'):
            sort_field = sort_field[1:]

        return queryset.order_by(sort_field)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Add customer services for filtering
        context['customer_services'] = CustomerService.objects.all()

        # Add sorting information
        sort_field = self.request.GET.get('sort', 'id')
        if sort_field.startswith('-'):
            sort_field = sort_field[1:]
            sort_direction = 'desc'
        else:
            sort_direction = 'asc'

        context.update({
            'current_sort': {
                'field': sort_field,
                'direction': sort_direction
            },
            'query_params': self.request.GET.copy(),
        })

        return context

class RuleGroupDetailView(LoginRequiredMixin, DetailView):
    model = RuleGroup
    template_name = 'rules/rule_group_detail.html'
    context_object_name = 'rule_group'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get all rules for this group with ordering
        context['rules'] = self.object.rules.all().order_by('field', 'operator')

        # Add summary statistics
        rules = context['rules']
        context.update({
            'total_rules': rules.count(),
            'rules_by_field': {
                field: rules.filter(field=field[0]).count()
                for field in Rule.FIELD_CHOICES
            },
            'rules_by_operator': {
                operator: rules.filter(operator=operator[0]).count()
                for operator in Rule.OPERATOR_CHOICES
            }
        })
        return context

class RuleGroupCreateView(LoginRequiredMixin, CreateView):
    model = RuleGroup
    form_class = RuleGroupForm
    template_name = 'rules/rule_group_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create Rule Group'
        context['submit_text'] = 'Create Group'
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Rule group created successfully.')
        return response

    def get_success_url(self):
        return reverse('rules:rule_group_detail', kwargs={'pk': self.object.pk})

class RuleGroupUpdateView(LoginRequiredMixin, UpdateView):
    model = RuleGroup
    form_class = RuleGroupForm
    template_name = 'rules/rule_group_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Rule Group'
        context['submit_text'] = 'Save Changes'
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Rule group updated successfully.')
        return response

    def get_success_url(self):
        return reverse('rules:rule_group_detail', kwargs={'pk': self.object.pk})

class RuleGroupDeleteView(LoginRequiredMixin, DeleteView):
    model = RuleGroup
    success_url = reverse_lazy('rules:rule_group_list')

    def delete(self, request, *args, **kwargs):
        group = self.get_object()
        result = super().delete(request, *args, **kwargs)
        messages.success(request, f'Rule group "{group}" deleted successfully.')
        return result

    def get_success_url(self):
        return self.success_url

class RuleCreateView(LoginRequiredMixin, CreateView):
    model = Rule
    form_class = RuleForm
    template_name = 'rules/rule_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        group = get_object_or_404(RuleGroup, pk=self.kwargs['group_id'])
        context.update({
            'group': group,
            'title': 'Create Rule',
            'submit_text': 'Create Rule',
            'field_choices': Rule.FIELD_CHOICES,
            'operator_choices': Rule.OPERATOR_CHOICES,
        })
        return context

    def form_valid(self, form):
        form.instance.rule_group_id = self.kwargs['group_id']
        response = super().form_valid(form)
        messages.success(self.request, 'Rule created successfully.')
        return response

    def get_success_url(self):
        return reverse('rules:rule_group_detail', kwargs={'pk': self.kwargs['group_id']})

class RuleUpdateView(LoginRequiredMixin, UpdateView):
    model = Rule
    form_class = RuleForm
    template_name = 'rules/rule_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'group': self.object.rule_group,
            'title': 'Edit Rule',
            'submit_text': 'Save Changes',
            'field_choices': Rule.FIELD_CHOICES,
            'operator_choices': Rule.OPERATOR_CHOICES,
        })
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Rule updated successfully.')
        return response

    def get_success_url(self):
        return reverse('rules:rule_group_detail', kwargs={'pk': self.object.rule_group.pk})

class RuleDeleteView(LoginRequiredMixin, DeleteView):
    model = Rule
    template_name = 'rules/rule_confirm_delete.html'

    def delete(self, request, *args, **kwargs):
        rule = self.get_object()
        group_id = rule.rule_group.id
        result = super().delete(request, *args, **kwargs)
        messages.success(request, 'Rule deleted successfully.')
        return result

    def get_success_url(self):
        return reverse('rules:rule_group_detail', kwargs={'pk': self.object.rule_group.pk})

# API Views for dynamic form updates
def get_operator_choices(request):
    """Return valid operators for a given field"""
    field = request.GET.get('field')
    if not field:
        return JsonResponse({'error': 'Field parameter is required'}, status=400)

    # Define valid operators for each field type
    numeric_fields = ['weight_lb', 'line_items', 'total_item_qty', 'volume_cuft', 'packages']
    string_fields = ['reference_number', 'ship_to_name', 'ship_to_company', 'ship_to_city',
                     'ship_to_state', 'ship_to_country', 'carrier', 'notes']
    json_fields = ['sku_quantity']

    if field in numeric_fields:
        valid_operators = ['gt', 'lt', 'eq', 'ne', 'ge', 'le', 'in', 'ni']
    elif field in string_fields:
        valid_operators = ['eq', 'ne', 'contains', 'ncontains', 'startswith', 'endswith', 'in', 'ni']
    elif field in json_fields:
        valid_operators = ['contains', 'ncontains', 'in', 'ni']
    else:
        valid_operators = [op[0] for op in Rule.OPERATOR_CHOICES]

    operators = [
        {'value': op[0], 'label': op[1]}
        for op in Rule.OPERATOR_CHOICES
        if op[0] in valid_operators
    ]

    return JsonResponse({'operators': operators})

def validate_rule_value(request):
    """Validate a rule value for a given field and operator"""
    field = request.GET.get('field')
    operator = request.GET.get('operator')
    value = request.GET.get('value')

    if not all([field, operator, value]):
        return JsonResponse({'error': 'All parameters are required'}, status=400)

    try:
        # Create a temporary rule for validation
        rule = Rule(field=field, operator=operator, value=value)
        rule.clean()
        return JsonResponse({'valid': True})
    except Exception as e:
        return JsonResponse({'valid': False, 'error': str(e)})