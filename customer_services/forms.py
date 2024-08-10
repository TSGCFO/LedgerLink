from django import forms
from .models import CustomerService


class CustomerServiceForm(forms.ModelForm):
    class Meta:
        model = CustomerService
        fields = [
            'customer', 'service', 'unit_price'
        ]
