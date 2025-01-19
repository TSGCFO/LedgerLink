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
            'order_date': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'w-full px-4 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:text-white'
                }
            ),
            'customer': forms.Select(
                attrs={
                    'class': 'w-full px-4 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:text-white'
                }
            ),
            'status': forms.Select(
                attrs={
                    'class': 'w-full px-4 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:text-white'
                }
            ),
            'priority': forms.Select(
                attrs={
                    'class': 'w-full px-4 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:text-white'
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'w-full px-4 py-2 border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm'

    def clean_sku_quantity(self):
        sku_quantity = self.cleaned_data.get('sku_quantity')
        if sku_quantity:
            try:
                # Handle already parsed JSON or string input
                if isinstance(sku_quantity, str):
                    # Remove any escaped quotes
                    sku_quantity = sku_quantity.replace('\\"', '"')
                    data = json.loads(sku_quantity)
                else:
                    data = sku_quantity

                # Validate structure
                if not isinstance(data, list):
                    raise forms.ValidationError("SKU quantity must be a list of items")

                # Clean and validate each item
                cleaned_data = []
                for item in data:
                    if not isinstance(item, dict):
                        raise forms.ValidationError("Each SKU item must be an object")
                    if 'sku' not in item or 'quantity' not in item:
                        raise forms.ValidationError("Each SKU item must have 'sku' and 'quantity' fields")

                    # Clean and validate SKU
                    sku = str(item['sku']).strip()
                    if not sku:
                        raise forms.ValidationError("SKU cannot be empty")

                    # Clean and validate quantity
                    try:
                        quantity = float(item['quantity'])
                        if quantity <= 0:
                            raise forms.ValidationError("Quantity must be a positive number")
                    except (TypeError, ValueError):
                        raise forms.ValidationError("Invalid quantity value")

                    cleaned_data.append({
                        'sku': sku,
                        'quantity': quantity
                    })

                # Store as a clean JSON string
                return json.dumps(cleaned_data)

            except json.JSONDecodeError:
                raise forms.ValidationError("Invalid JSON format")
            except Exception as e:
                raise forms.ValidationError(f"Invalid data format: {str(e)}")
        return sku_quantity