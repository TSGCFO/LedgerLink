from django.contrib import admin
from .models import Customer, Order, Service, CustomerService, Insert, Product, ServiceLog, Material, Box, BoxPrice
from .forms import InsertForm
import json

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

    def changelist_view(self, request, extra_context=None):
        # Ensure sku_quantity is correctly handled
        for order in Order.objects.all():
            if isinstance(order.sku_quantity, str):
                order.sku_quantity = json.loads(order.sku_quantity)
            elif isinstance(order.sku_quantity, list):
                order.sku_quantity = json.dumps(order.sku_quantity)
        return super().changelist_view(request, extra_context)


# Register all the models with the admin site
admin.site.register(Customer)
admin.site.register(Service)
admin.site.register(CustomerService)
admin.site.register(Insert, InsertAdmin)
admin.site.register(Product)
admin.site.register(ServiceLog)
admin.site.register(Order, OrderAdmin)
admin.site.register(Material)
admin.site.register(Box)
admin.site.register(BoxPrice)