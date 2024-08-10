from django import forms
from .models import Order


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [
            'transaction_id', 'customer', 'reference_number', 'close_date', 'ship_to_name',
            'ship_to_company', 'ship_to_address', 'ship_to_address2', 'ship_to_city',
            'ship_to_state', 'ship_to_zip', 'ship_to_country', 'weight_lb', 'line_items',
            'sku_quantity', 'total_item_qty', 'volume_cuft', 'packages', 'notes', 'carrier'
        ]
