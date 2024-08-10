# rules/forms.py

from django import forms
from .models import RuleGroup, Rule


class RuleGroupForm(forms.ModelForm):
    class Meta:
        model = RuleGroup
        fields = ['customer_service', 'logic_operator']


class RuleForm(forms.ModelForm):
    class Meta:
        model = Rule
        fields = ['rule_group', 'field', 'operator', 'value', 'adjustment_amount']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'initial' in kwargs and 'rule_group' in kwargs['initial']:
            rule_group = kwargs['initial']['rule_group']
            customer_service = rule_group.customer_service
            self.fields['adjustment_amount'].initial = customer_service.unit_price
