# billing/forms.py

from django import forms
from customers.models import Customer
from orders.models import Order

class BillingForm(forms.Form):
    customer = forms.ModelChoiceField(queryset=Customer.objects.all(), label="Customer")
    orders = forms.ModelMultipleChoiceField(queryset=Order.objects.all(), label="Orders", widget=forms.CheckboxSelectMultiple)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['customer'].queryset = Customer.objects.all()
        self.fields['orders'].queryset = Order.objects.all()
