from django import forms
from .models import Customer


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['company_name', 'legal_business_name', 'email', 'phone', 'address', 'city', 'state', 'zip', 'country', 'business_type']
