from django import forms
from .models import Insert, Product

class ProductUploadForm(forms.Form):
    file = forms.FileField()


class InsertForm(forms.ModelForm):
    sku = forms.ModelChoiceField(queryset=Product.objects.all(), required=True)

    class Meta:
        model = Insert
        fields = ['sku', 'customer', 'insert_name', 'insert_quantity']
