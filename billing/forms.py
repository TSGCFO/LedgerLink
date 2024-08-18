from django import forms
from .models import Invoice

class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['customer', 'order', 'due_date', 'total_amount', 'currency', 'status']
