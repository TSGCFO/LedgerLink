from django import forms
from customers.models import Customer

class BillingForm(forms.Form):
    customer = forms.ModelChoiceField(
        queryset=Customer.objects.all(),
        label="Customer",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    start_date = forms.DateField(
        label="Start Date",
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    end_date = forms.DateField(
        label="End Date",
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")

        if start_date and end_date and start_date > end_date:
            raise forms.ValidationError("End date should be after start date.")

        return cleaned_data