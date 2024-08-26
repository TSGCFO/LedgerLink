from django.db import models
from customers.models import Customer
from orders.models import Order

# Create your models here.
class Invoice(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    invoice_date = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    details = models.JSONField(null=True, blank=True)  # Store detailed invoice breakdown as JSON

    def __str__(self):
        return f"Invoice {self.id} for {self.customer.company_name} on {self.invoice_date}"

    # billing/models.py


class BillingLog(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    log_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50)  # e.g., "success", "failed"
    message = models.TextField(null=True, blank=True)  # Store additional details or error messages

    def __str__(self):
        return f"BillingLog {self.id} for {self.customer.company_name} - {self.status}"

# billing/models.py


class BillingConfiguration(models.Model):
    name = models.CharField(max_length=100, unique=True)
    value = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Billing Configuration: {self.name}"
