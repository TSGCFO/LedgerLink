from django.contrib import admin
from .models import Order


# Register your models here.

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'transaction_id', 'customer', 'reference_number', 'close_date', 'total_item_qty',)
    search_fields = ('transaction_id', 'customer__company_name', 'reference_number')
