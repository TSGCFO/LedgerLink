# Create your models here.
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from customers.models import Customer
from orders.models import Order

class BillingReport(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    generated_at = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    report_data = models.JSONField()
    
    # Add audit fields
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_reports'
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='updated_reports'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-generated_at']
        verbose_name = 'Billing Report'
        verbose_name_plural = 'Billing Reports'
        indexes = [
            models.Index(fields=['customer', 'start_date', 'end_date']),
            models.Index(fields=['generated_at']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"Report for {self.customer.company_name} ({self.start_date} to {self.end_date})"

    def clean(self):
        if self.start_date and self.end_date:
            if self.start_date > self.end_date:
                raise ValidationError("Start date must be before end date")
            
            date_diff = (self.end_date - self.start_date).days
            if date_diff > settings.MAX_REPORT_DATE_RANGE:
                raise ValidationError(f"Date range cannot exceed {settings.MAX_REPORT_DATE_RANGE} days")
            
            if self.start_date > timezone.now().date():
                raise ValidationError("Start date cannot be in the future")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

class BillingReportDetail(models.Model):
    report = models.ForeignKey(
        BillingReport,
        on_delete=models.CASCADE,
        related_name='details'
    )
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    service_breakdown = models.JSONField()
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )

    class Meta:
        verbose_name = 'Billing Report Detail'
        verbose_name_plural = 'Billing Report Details'
        indexes = [
            models.Index(fields=['report', 'order']),
            models.Index(fields=['total_amount']),
        ]

    def __str__(self):
        return f"Detail for {self.report} - Order {self.order.transaction_id}"