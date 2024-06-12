from django.contrib import admin
from .models import Customer, Order, Service, CustomerService, Insert, Product, ServiceLog, Material, Box, BoxPrice
from .forms import InsertForm

# Custom Admin class for Insert model
class InsertAdmin(admin.ModelAdmin):
    form = InsertForm
    list_display = ('sku', 'customer', 'insert_name', 'insert_quantity', 'created_at', 'updated_at')

# Custom Admin class for Order model
class OrderAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Order._meta.fields]

    class Media:
        css = {
            'all': ('billing/css/custom_admin.css',)
        }


# Register all the models with the admin site
admin.site.register(Customer)
admin.site.register(Service)
admin.site.register(CustomerService)
admin.site.register(Insert, InsertAdmin)  # Use the custom admin class for Insert
admin.site.register(Product)
admin.site.register(ServiceLog)
admin.site.register(Order, OrderAdmin)  # Use the custom admin class for Order
admin.site.register(Material)
admin.site.register(Box)
admin.site.register(BoxPrice)
