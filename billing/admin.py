from django.contrib import admin
from .models import Invoice, BillingLog, BillingConfiguration

# Register your models here.
# billing/admin.py


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'invoice_date', 'total_amount')
    search_fields = ('customer__company_name', 'invoice_date')
    list_filter = ('invoice_date',)
    readonly_fields = ('invoice_date',)

@admin.register(BillingLog)
class BillingLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'order', 'log_date', 'status')
    search_fields = ('customer__company_name', 'order__reference_number', 'status')
    list_filter = ('log_date', 'status')
    readonly_fields = ('log_date',)

@admin.register(BillingConfiguration)
class BillingConfigurationAdmin(admin.ModelAdmin):
    list_display = ('name', 'value', 'description')
    search_fields = ('name', 'value')
