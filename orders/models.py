# orders/models.py

from django.db import models
from customers.models import Customer


class Order(models.Model):
    PRIORITY_CHOICES = [ # Choices for the priority field in the Order model
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]
    STATUS_CHOICES = [ # Choices for the status field in the Order model
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    transaction_id = models.BigIntegerField(primary_key=True)  # Externally assigned
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    close_date = models.DateTimeField(blank=True, null=True)
    reference_number = models.CharField(max_length=100)
    ship_to_name = models.CharField(max_length=100, blank=True, null=True)
    ship_to_company = models.CharField(max_length=100, blank=True, null=True)
    ship_to_address = models.CharField(max_length=200, blank=True, null=True)
    ship_to_address2 = models.CharField(max_length=200, blank=True, null=True)
    ship_to_city = models.CharField(max_length=100, blank=True, null=True)
    ship_to_state = models.CharField(max_length=50, blank=True, null=True)
    ship_to_zip = models.CharField(max_length=20, blank=True, null=True)
    ship_to_country = models.CharField(max_length=50, blank=True, null=True)
    weight_lb = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    line_items = models.IntegerField(blank=True, null=True)
    sku_quantity = models.JSONField(blank=True, null=True)
    total_item_qty = models.IntegerField(blank=True, null=True)
    volume_cuft = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    packages = models.IntegerField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    carrier = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft'
    )
    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='medium'
    )

    def __str__(self):
        return f"Order {self.transaction_id} for {self.customer}"
    
    def get_sku_details(self, exclude_skus=None):
        """Get detailed SKU information including cases and picks"""
        sku_view = OrderSKUView.objects.filter(transaction_id=self.transaction_id)
        if exclude_skus:
            sku_view = sku_view.exclude(sku_name__in=exclude_skus)
        return sku_view

    def get_total_cases(self, exclude_skus=None):
        """Get total cases across all SKUs, optionally excluding specific SKUs"""
        return self.get_sku_details(exclude_skus).aggregate(
            total_cases=models.Sum('cases')
        )['total_cases'] or 0

    def get_total_picks(self, exclude_skus=None):
        """Get total picks across all SKUs, optionally excluding specific SKUs"""
        return self.get_sku_details(exclude_skus).aggregate(
            total_picks=models.Sum('picks')
        )['total_picks'] or 0

    def has_only_excluded_skus(self, exclude_skus):
        """Check if order only contains SKUs from the excluded list"""
        return not self.get_sku_details().exclude(
            sku_name__in=exclude_skus
        ).exists()

    def get_case_summary(self, exclude_skus=None):
        """Get a summary of cases and picks by SKU"""
        details = self.get_sku_details(exclude_skus)
        return {
            'total_cases': self.get_total_cases(exclude_skus),
            'total_picks': self.get_total_picks(exclude_skus),
            'sku_breakdown': list(details.values(
                'sku_name', 'cases', 'picks', 'case_size', 'case_unit'
            ))
        }


class OrderSKUView(models.Model):
    transaction_id = models.BigIntegerField(primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    close_date = models.DateTimeField(blank=True, null=True)
    reference_number = models.CharField(max_length=100)
    ship_to_name = models.CharField(max_length=100, blank=True, null=True)
    ship_to_company = models.CharField(max_length=100, blank=True, null=True)
    ship_to_address = models.CharField(max_length=200, blank=True, null=True)
    ship_to_address2 = models.CharField(max_length=200, blank=True, null=True)
    ship_to_city = models.CharField(max_length=100, blank=True, null=True)
    ship_to_state = models.CharField(max_length=50, blank=True, null=True)
    ship_to_zip = models.CharField(max_length=20, blank=True, null=True)
    ship_to_country = models.CharField(max_length=50, blank=True, null=True)
    weight_lb = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    line_items = models.IntegerField(blank=True, null=True)
    total_item_qty = models.IntegerField(blank=True, null=True)
    volume_cuft = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    packages = models.IntegerField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    carrier = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(max_length=20)
    priority = models.CharField(max_length=20)
    sku_name = models.CharField(max_length=100)
    sku_count = models.IntegerField()
    cases = models.IntegerField()
    picks = models.IntegerField()
    case_size = models.IntegerField(null=True)
    case_unit = models.CharField(max_length=50, null=True)

    class Meta:
        managed = False
        db_table = 'orders_sku_view'

    def __str__(self):
        return f"Order {self.transaction_id} - {self.sku_name}: {self.cases} cases, {self.picks} picks"

