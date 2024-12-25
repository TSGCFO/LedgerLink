from django import forms
from .models import Order
import json

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [
            'transaction_id', 'customer', 'reference_number', 'close_date',
            'ship_to_name', 'ship_to_company', 'ship_to_address', 'ship_to_address2',
            'ship_to_city', 'ship_to_state', 'ship_to_zip', 'ship_to_country',
            'weight_lb', 'line_items', 'sku_quantity', 'total_item_qty',
            'volume_cuft', 'packages', 'notes', 'carrier'
        ]
        widgets = {
            'close_date': forms.DateTimeInput(
                attrs={'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M'
            ),
            'sku_quantity': forms.Textarea(
                attrs={
                    'rows': 4,
                    'placeholder': '[{"sku": "ABC123", "quantity": 5}]'
                }
            ),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def clean_sku_quantity(self):
        sku_quantity = self.cleaned_data.get('sku_quantity')
        if sku_quantity:
            try:
                # Validate JSON format
                if isinstance(sku_quantity, str):
                    data = json.loads(sku_quantity)
                else:
                    data = sku_quantity

                # Validate structure
                if not isinstance(data, list):
                    raise forms.ValidationError("SKU quantity must be a list of items")

                for item in data:
                    if not isinstance(item, dict):
                        raise forms.ValidationError("Each SKU item must be an object")
                    if 'sku' not in item or 'quantity' not in item:
                        raise forms.ValidationError("Each SKU item must have 'sku' and 'quantity' fields")
                    if not isinstance(item['quantity'], (int, float)) or item['quantity'] <= 0:
                        raise forms.ValidationError("Quantity must be a positive number")

                # Format JSON string
                return json.dumps(data, indent=2)
            except json.JSONDecodeError:
                raise forms.ValidationError("Invalid JSON format")
        return sku_quantity