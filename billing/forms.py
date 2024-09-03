# billing/forms.py

from django import forms
from customers.models import Customer
from orders.models import Order

class BillingForm(forms.Form):
    customer = forms.ModelChoiceField(queryset=Customer.objects.all(), label="Customer")
    start_date = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}), label="Start Date")
    end_date = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}), label="End Date")
    orders = forms.ModelMultipleChoiceField(
        queryset=Order.objects.none(),  # Start with an empty queryset
        label="Orders",
        widget=forms.CheckboxSelectMultiple,
    )

    def __init__(self, *args, **kwargs):
        customer = kwargs.pop('customer', None)
        start_date = kwargs.pop('start_date', None)
        end_date = kwargs.pop('end_date', None)
        super().__init__(*args, **kwargs)

        if customer:
            orders_queryset = Order.objects.filter(customer=customer)
            if start_date and end_date:
                orders_queryset = orders_queryset.filter(order_date__range=(start_date, end_date))
            self.fields['orders'].queryset = orders_queryset
