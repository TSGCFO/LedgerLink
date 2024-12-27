from django.urls import path
from . import views

app_name = 'rules'

urlpatterns = [
    # Existing URLs
    path('', views.RuleGroupListView.as_view(), name='rule_group_list'),
    path('group/create/', views.RuleGroupCreateView.as_view(), name='create_rule_group'),
    path('group/<int:pk>/', views.RuleGroupDetailView.as_view(), name='rule_group_detail'),
    path('group/<int:pk>/edit/', views.RuleGroupUpdateView.as_view(), name='edit_rule_group'),
    path('group/<int:pk>/delete/', views.RuleGroupDeleteView.as_view(), name='delete_rule_group'),
    path('group/<int:group_id>/rule/create/', views.RuleCreateView.as_view(), name='create_rule'),
    path('rule/<int:pk>/edit/', views.RuleUpdateView.as_view(), name='edit_rule'),
    path('rule/<int:pk>/delete/', views.RuleDeleteView.as_view(), name='delete_rule'),

    # API endpoints
    path('api/operators/', views.get_operator_choices, name='get_operators'),
    path('api/validate/', views.validate_rule_value, name='validate_rule'),
]