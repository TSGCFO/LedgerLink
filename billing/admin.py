from django.contrib import admin

from billing.models import Charge, Invoice


# Register your models here.
@admin.register(Charge)
class ChargeAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'service', 'amount', 'currency', 'invoiced')
    list_filter = ('currency', 'invoiced')
    search_fields = ('order__transaction_id', 'service__name')
    list_per_page = 10


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'total_amount', 'currency', 'status')
    list_filter = ('currency', 'status')
    search_fields = ('order__transaction_id',)
    list_per_page = 10
