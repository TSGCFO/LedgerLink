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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Dynamically adjust the widget for the 'value' field based on the selected 'field' and 'operator'
        if 'field' in self.data:
            field_value = self.data.get('field')
            operator_value = self.data.get('operator')

            # Handle dynamic field adjustments based on both field and operator
            if field_value == 'sku_quantity':
                if operator_value in ['contains', 'in', 'ni']:
                    self.fields['value'] = forms.CharField(
                        widget=forms.Textarea,
                        help_text='Enter the SKUs in a list format, separated by semicolons.'
                    )
                elif operator_value in ['eq', 'ne']:
                    self.fields['value'] = forms.CharField(
                        help_text='Enter the SKU in a JSON format.'
                    )
            elif field_value in ['weight_lb', 'line_items', 'total_item_qty', 'volume_cuft', 'packages']:
                self.fields['value'] = forms.DecimalField(
                    help_text='Enter a numeric value.',
                    min_value=0
                )
            else:
                self.fields['value'] = forms.CharField(
                    help_text='Enter the condition value.'
                )

    def clean_value(self):
        value = self.cleaned_data.get('value', '')

        # If value is a list (from a ChoiceField with multiple selection), join it back as a semicolon-separated string
        if isinstance(value, list):
            value = ";".join(value)

        # Further clean value based on field/operator logic
        field = self.cleaned_data.get('field')
        operator = self.cleaned_data.get('operator')

        # Basic validation based on operator
        if operator in ['gt', 'lt', 'ge', 'le', 'eq', 'ne']:
            if field in ['weight_lb', 'line_items', 'total_item_qty', 'volume_cuft', 'packages']:
                try:
                    float(value)
                except ValueError:
                    raise forms.ValidationError('This field requires a numeric value.')

        return value
