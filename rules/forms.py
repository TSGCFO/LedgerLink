from django import forms
from .models import RuleGroup, Rule

class RuleGroupForm(forms.ModelForm):
    class Meta:
        model = RuleGroup
        fields = ['customer_service', 'logic_operator']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['customer_service'].widget.attrs.update({'class': 'form-select'})
        self.fields['logic_operator'].widget.attrs.update({'class': 'form-select'})

class RuleForm(forms.ModelForm):
    class Meta:
        model = Rule
        fields = ['field', 'operator', 'value', 'adjustment_amount']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['field'].widget.attrs.update({'class': 'form-select'})
        self.fields['operator'].widget.attrs.update({'class': 'form-select'})
        self.fields['value'].widget.attrs.update({'class': 'form-control'})
        self.fields['adjustment_amount'].widget.attrs.update({
            'class': 'form-control',
            'step': '0.01'
        })