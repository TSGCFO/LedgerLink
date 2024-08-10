# customer_services/models.py

from django.db import models
from customers.models import Customer
from services.models import Service


class CustomerService(models.Model):
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)

    class Meta:
        unique_together = (('customer', 'service'),)

    def __str__(self):
        return f"{self.customer} - {self.service}"
