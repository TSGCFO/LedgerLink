from django.contrib import admin
from .models import Customer, Order, Service, CustomerService, Insert, Product, ServiceLog

admin.site.register(Customer)
admin.site.register(Service)
admin.site.register(CustomerService)
admin.site.register(Insert)
admin.site.register(Product)
admin.site.register(ServiceLog)
admin.site.register(Order)
# Register your models here.
