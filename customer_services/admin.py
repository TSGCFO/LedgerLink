from django.contrib import admin
from .models import CustomerService


# Register your models here.

@admin.register(CustomerService)
class CustomerServiceAdmin(admin.ModelAdmin):
    list_display = ('customer', 'service', 'unit_price', 'created_at', 'updated_at')
    search_fields = ('customer__company_name', 'service__service_name')
