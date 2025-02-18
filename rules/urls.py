# rules/urls.py

from django.urls import path
from . import views

app_name = 'rules'

urlpatterns = [
    # API endpoints
    path('api/groups/', views.RuleGroupAPIView.as_view(), name='api_rule_groups'),
    path('operators/', views.get_operator_choices, name='get_operators'),
    path('validate-conditions/', views.validate_conditions, name='validate_conditions'),
    path('validate-calculations/', views.validate_calculations, name='validate_calculations'),
    path('conditions-schema/', views.get_conditions_schema, name='get_conditions_schema'),
    path('calculations-schema/', views.get_calculations_schema, name='get_calculations_schema'),
    path('fields/', views.get_available_fields, name='get_available_fields'),
    path('calculation-types/', views.get_calculation_types, name='get_calculation_types'),
    path('validate-rule-value/', views.validate_rule_value, name='validate_rule_value'),
    path('group/<int:group_id>/rules/', views.get_rules, name='get_rules'),
    path('group/<int:group_id>/rule/create/api/', views.create_or_update_rule, name='api_create_rule'),
    path('rule/<int:pk>/edit/api/', views.create_or_update_rule, name='api_update_rule'),
    path('rule/<int:pk>/delete/api/', views.delete_rule, name='api_delete_rule'),
    path('group/<int:pk>/delete/api/', views.delete_rule_group, name='api_delete_rule_group'),
    path('group/<int:group_id>/advanced-rules/', views.get_advanced_rules, name='get_advanced_rules'),

    # Rule Group URLs
    path('',
         views.RuleGroupListView.as_view(),
         name='rule_group_list'),
    path('group/create/',
         views.RuleGroupCreateView.as_view(),
         name='create_rule_group'),
    path('group/<int:pk>/',
         views.RuleGroupDetailView.as_view(),
         name='rule_group_detail'),
    path('group/<int:pk>/edit/',
         views.RuleGroupUpdateView.as_view(),
         name='edit_rule_group'),
    path('group/<int:pk>/delete/',
         views.RuleGroupDeleteView.as_view(),
         name='delete_rule_group'),

    # Basic Rule URLs
    path('group/<int:group_id>/rule/create/',
         views.RuleCreateView.as_view(),
         name='create_rule'),
    path('rule/<int:pk>/edit/',
         views.RuleUpdateView.as_view(),
         name='edit_rule'),
    path('rule/<int:pk>/delete/',
         views.RuleDeleteView.as_view(),
         name='delete_rule'),

    # Advanced Rule URLs
    path('group/<int:group_id>/advanced-rule/create/',
         views.AdvancedRuleCreateView.as_view(),
         name='create_advanced_rule'),
    path('advanced-rule/<int:pk>/edit/',
         views.AdvancedRuleUpdateView.as_view(),
         name='edit_advanced_rule'),
    path('advanced-rule/<int:pk>/delete/',
         views.AdvancedRuleDeleteView.as_view(),
         name='delete_advanced_rule'),
    path('group/<int:group_id>/skus/', views.get_customer_skus, name='get_customer_skus'),
]