from django import forms
from .models import RuleGroup, Rule


class RuleGroupForm(forms.ModelForm):
    class Meta:
        model = RuleGroup
        fields = ['customer_service', 'logic_operator']
        labels = {
            'customer_service': 'Customer Service',
            'logic_operator': 'Logical Operator'
        }
        help_texts = {
            'customer_service': 'Select the customer service this rule applies to.',
            'logic_operator': 'Choose how multiple rules should be combined (AND, OR, etc.).'
        }


class RuleForm(forms.ModelForm):
    class Meta:
        model = Rule
        fields = ['rule_group', 'field', 'operator', 'value', 'adjustment_amount']
        labels = {
            'rule_group': 'Pricing Rule Group',
            'field': 'Condition Field',
            'operator': 'Condition Operator',
            'value': 'Condition Value',
            'adjustment_amount': 'Price Adjustment'
        }
        help_texts = {
            'rule_group': 'Select the group of rules this rule belongs to.',
            'field': 'Choose the attribute this rule applies to, such as SKU or Quantity.',
            'operator': 'Select the condition for the rule, like "equals" or "greater than".',
            'value': 'Specify the value that matches the condition (e.g., specific SKU, quantity).',
            'adjustment_amount': 'Specify the amount to adjust the price by for this rule.'
        }
        widgets = {
            'operator': forms.Select(choices=[
                ('=', 'is equal to'),
                ('>=', 'is greater than or equal to'),
                ('<=', 'is less than or equal to'),
                ('!=', 'is not equal to'),
                ('in', 'is in list'),
                ('not in', 'is not in list')
            ]),
            'field': forms.Select(choices=[
                ('sku', 'SKU'),
                ('quantity', 'Quantity'),
                ('case_picks', 'Case Picks')
            ])
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Dynamically adjust the widget for the 'value' field based on the selected 'field'
        if 'field' in self.data:
            field_value = self.data.get('field')
            if field_value == 'sku':
                # Assuming SKUs are predefined, convert to a dropdown
                self.fields['value'] = forms.ChoiceField(choices=[('SKU1', 'SKU1'), ('SKU2', 'SKU2')],
                                                         help_text='Select the SKU')
            elif field_value == 'quantity':
                # For quantity, provide a numeric input
                self.fields['value'] = forms.IntegerField(min_value=1, help_text='Enter the quantity')
            elif field_value == 'case_picks':
                # Case picks might also be a number, use IntegerField
                self.fields['value'] = forms.IntegerField(min_value=1, help_text='Enter the number of case picks')
            else:
                # Fallback to text input
                self.fields['value'] = forms.CharField(help_text='Enter the condition value')

        if 'initial' in kwargs and 'rule_group' in kwargs['initial']:
            rule_group = kwargs['initial']['rule_group']
            customer_service = rule_group.customer_service
            self.fields['adjustment_amount'].initial = customer_service.unit_price

    def clean_value(self):
        value = self.cleaned_data.get('value', '')

        # If value is a list (from a ChoiceField with multiple selection), join it back as a semicolon-separated string
        if isinstance(value, list):
            value = ";".join(value)

        return value
