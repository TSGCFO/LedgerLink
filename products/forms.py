# products/forms.py
from django import forms
from .models import Product


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'sku', 'labeling_unit_1', 'labeling_quantity_1', 'labeling_unit_2', 'labeling_quantity_2',
            'labeling_unit_3', 'labeling_quantity_3', 'labeling_unit_4', 'labeling_quantity_4',
            'labeling_unit_5', 'labeling_quantity_5', 'customer'
        ]

    def clean_labeling_quantity_1(self):
        quantity = self.cleaned_data.get('labeling_quantity_1')
        if quantity is not None and quantity < 0:
            raise forms.ValidationError("Labeling quantity 1 must be greater than or equal to 0.")
        return quantity

    def clean_labeling_quantity_2(self):
        quantity = self.cleaned_data.get('labeling_quantity_2')
        if quantity is not None and quantity < 0:
            raise forms.ValidationError("Labeling quantity 2 must be greater than or equal to 0.")
        return quantity

    def clean_labeling_quantity_3(self):
        quantity = self.cleaned_data.get('labeling_quantity_3')
        if quantity is not None and quantity < 0:
            raise forms.ValidationError("Labeling quantity 3 must be greater than or equal to 0.")
        return quantity

    def clean_labeling_quantity_4(self):
        quantity = self.cleaned_data.get('labeling_quantity_4')
        if quantity is not None and quantity < 0:
            raise forms.ValidationError("Labeling quantity 4 must be greater than or equal to 0.")
        return quantity

    def clean_labeling_quantity_5(self):
        quantity = self.cleaned_data.get('labeling_quantity_5')
        if quantity is not None and quantity < 0:
            raise forms.ValidationError("Labeling quantity 5 must be greater than or equal to 0.")
        return quantity


class ProductUploadForm(forms.Form):
    file = forms.FileField()
