# rules/forms.py

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import json

from .models import RuleGroup, Rule, AdvancedRule
from customer_services.models import CustomerService
from products.models import Product


class RuleGroupForm(forms.ModelForm):
    class Meta:
        model = RuleGroup
        fields = ['customer_service', 'logic_operator']
        widgets = {
            'customer_service': forms.Select(attrs={
                'class': 'form-select',
                'data-controller': 'select'
            }),
            'logic_operator': forms.Select(attrs={
                'class': 'form-select',
                'data-controller': 'select'
            })
        }


class RuleForm(forms.ModelForm):
    class Meta:
        model = Rule
        fields = ['field', 'operator', 'value', 'adjustment_amount']
        widgets = {
            'field': forms.Select(attrs={
                'class': 'form-select',
                'data-controller': 'rule-field'
            }),
            'operator': forms.Select(attrs={
                'class': 'form-select',
                'data-controller': 'rule-operator'
            }),
            'value': forms.TextInput(attrs={
                'class': 'form-control',
                'data-controller': 'rule-value'
            }),
            'adjustment_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['field'].widget.attrs['data-operators-url'] = 'rules:get_operators'

        if self.instance and self.instance.field == 'sku_quantity':
            self.fields['value'].widget = forms.Select(attrs={
                'class': 'form-select',
                'multiple': 'multiple',
                'data-controller': 'sku-selector'
            })
            if self.instance.rule_group:
                customer_service = self.instance.rule_group.customer_service
                self.fields['value'].choices = self.get_sku_choices(customer_service)

    def get_sku_choices(self, customer_service):
        """Get SKU choices for the customer"""
        skus = Product.objects.filter(
            customer=customer_service.customer
        ).values_list('sku', flat=True)
        return [(sku, sku) for sku in skus]  # Use SKU as both value and label

    def clean(self):
        cleaned_data = super().clean()
        field = cleaned_data.get('field')
        operator = cleaned_data.get('operator')
        value = cleaned_data.get('value')

        if field == 'sku_count':
            # Handle SKU count validation
            try:
                float(value)
            except (ValueError, TypeError):
                raise ValidationError(_('SKU count must be a number'))

        elif field == 'sku_name':
            # Handle SKU name validation
            if operator in ['gt', 'lt', 'ge', 'le']:
                raise ValidationError(_('Invalid operator for SKU name'))

        elif field == 'sku_quantity':
            # Handle SKU validation
            if operator in ['contains', 'ncontains', 'only_contains']:
                if not value:
                    raise ValidationError(_('At least one SKU must be selected'))

                # If multiple SKUs were selected, they come as a list
                if isinstance(value, (list, tuple)):
                    cleaned_data['value'] = ';'.join(value)

        return cleaned_data


class AdvancedRuleForm(forms.ModelForm):
    class Meta:
        model = AdvancedRule
        fields = ['field', 'operator', 'value', 'adjustment_amount', 'conditions', 'calculations']
        widgets = {
            'field': forms.Select(attrs={
                'class': 'form-select',
                'data-controller': 'rule-field'
            }),
            'operator': forms.Select(attrs={
                'class': 'form-select',
                'data-controller': 'rule-operator'
            }),
            'value': forms.TextInput(attrs={
                'class': 'form-control',
                'data-controller': 'rule-value'
            }),
            'adjustment_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01'
            }),
            'conditions': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'data-controller': 'json-editor'
            }),
            'calculations': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'data-controller': 'json-editor'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['field'].widget.attrs['data-operators-url'] = 'rules:get_operators'

        if self.instance and self.instance.field == 'sku_quantity':
            self.setup_sku_selector()

    def setup_sku_selector(self):
        """Set up the SKU selector for SKU quantity fields"""
        self.fields['value'].widget = forms.Select(attrs={
            'class': 'form-select',
            'multiple': 'multiple',
            'data-controller': 'sku-selector'
        })
        if self.instance.rule_group:
            customer_service = self.instance.rule_group.customer_service
            self.fields['value'].choices = self.get_sku_choices(customer_service)

    def get_sku_choices(self, customer_service):
        """Get SKU choices for the customer"""
        skus = Product.objects.filter(
            customer=customer_service.customer
        ).values_list('sku', flat=True)
        return [(sku, sku) for sku in skus]  # Use SKU as both value and label

    def clean(self):
        cleaned_data = super().clean()
        field = cleaned_data.get('field')
        operator = cleaned_data.get('operator')
        value = cleaned_data.get('value')

        if field == 'sku_count':
            # Handle SKU count validation
            try:
                float(value)
            except (ValueError, TypeError):
                raise ValidationError(_('SKU count must be a number'))

        elif field == 'sku_name':
            # Handle SKU name validation
            if operator in ['gt', 'lt', 'ge', 'le']:
                raise ValidationError(_('Invalid operator for SKU name'))

        elif field == 'sku_quantity':
            if operator in ['contains', 'ncontains', 'only_contains']:
                if not value:
                    raise ValidationError(_('At least one SKU must be selected'))

                # If multiple SKUs were selected, they come as a list
                if isinstance(value, (list, tuple)):
                    cleaned_data['value'] = ';'.join(value)

        return cleaned_data

    def clean_conditions(self):
        """Validate the conditions JSON structure"""
        conditions = self.cleaned_data.get('conditions')

        try:
            if isinstance(conditions, str):
                conditions = json.loads(conditions)

            if not isinstance(conditions, dict):
                raise ValidationError(_("Conditions must be a JSON object"))

            return conditions

        except json.JSONDecodeError as e:
            raise ValidationError(_(f"Invalid JSON format: {str(e)}"))
        except Exception as e:
            raise ValidationError(_(f"Invalid conditions format: {str(e)}"))

    def clean_calculations(self):
        """Validate the calculations JSON structure"""
        calculations = self.cleaned_data.get('calculations')

        try:
            if isinstance(calculations, str):
                calculations = json.loads(calculations)

            if not isinstance(calculations, list):
                raise ValidationError(_("Calculations must be a JSON array"))

            return calculations

        except json.JSONDecodeError as e:
            raise ValidationError(_(f"Invalid JSON format: {str(e)}"))
        except Exception as e:
            raise ValidationError(_(f"Invalid calculations format: {str(e)}"))