# rules/urls.py

from django.urls import path
from . import views

app_name = 'rules'

urlpatterns = [
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

    # API endpoints
    path('api/operators/',
         views.get_operator_choices,
         name='get_operators'),
    path('api/customer-skus/<int:customer_service_id>/',
         views.get_customer_skus,
         name='get_customer_skus'),
    path('api/validate/conditions/',
         views.validate_conditions,
         name='validate_conditions'),
    path('api/validate/calculations/',
         views.validate_calculations,
         name='validate_calculations'),
    path('api/calculation-types/',
         views.get_calculation_types,
         name='get_calculation_types'),
]