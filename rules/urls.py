from django.urls import path
from . import views

urlpatterns = [
    path('rule-groups/', views.rule_group_list, name='rule_group_list'),
    path('rule-groups/create/', views.create_rule_group, name='create_rule_group'),
    path('rule-groups/<int:group_id>/', views.rule_group_detail, name='rule_group_detail'),
    path('rule-groups/<int:group_id>/add-rule/', views.create_rule, name='create_rule'),
]
