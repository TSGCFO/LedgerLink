# billing/models.py

from django.db import models
from django.contrib.postgres.fields import JSONField
from customers.models import Customer
from services.models import Service


class BillingCriteria(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    criteria = JSONField()  # Store criteria as a JSON object

    def __str__(self):
        return f"{self.customer.company_name} - {self.service.service_name}"
