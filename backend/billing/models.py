from django.db import models
from django.utils import timezone

class Customer(models.Model):
    customer_id = models.AutoField(primary_key=True)
    company_name = models.CharField(max_length=100)
    legal_business_name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100, unique=True)
    phone = models.CharField(max_length=20)
    address = models.CharField(max_length=200)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    zip = models.CharField(max_length=20)
    country = models.CharField(max_length=50)
    business_type = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.company_name

    class Meta:
        unique_together = ('email',)


class Service(models.Model):
    service_id = models.AutoField(primary_key=True)
    service_name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.service_name


class CustomerService(models.Model):
    customer_service_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.customer.company_name} - {self.service.service_name}'


class Insert(models.Model):
    insert_id = models.AutoField(primary_key=True)
    sku = models.CharField(max_length=100)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    insert_name = models.CharField(max_length=100)
    insert_quantity = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.insert_name


class Product(models.Model):
    sku = models.CharField(max_length=100, primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    labeling_unit_1 = models.CharField(max_length=50, blank=True, null=True)
    labeling_quantity_1 = models.IntegerField(blank=True, null=True)
    labeling_unit_2 = models.CharField(max_length=50, blank=True, null=True)
    labeling_quantity_2 = models.IntegerField(blank=True, null=True)
    labeling_unit_3 = models.CharField(max_length=50, blank=True, null=True)
    labeling_quantity_3 = models.IntegerField(blank=True, null=True)
    labeling_unit_4 = models.CharField(max_length=50, blank=True, null=True)
    labeling_quantity_4 = models.IntegerField(blank=True, null=True)
    labeling_unit_5 = models.CharField(max_length=50, blank=True, null=True)
    labeling_quantity_5 = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.sku


class ServiceLog(models.Model):
    log_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    sku = models.CharField(max_length=100)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)
    performed_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.customer.company_name} - {self.service.service_name} - {self.sku}'


class Order(models.Model):
    transaction_id = models.AutoField(primary_key=True)
    create_date = models.DateTimeField(auto_now_add=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    customer_name = models.CharField(max_length=100)
    reference_number = models.CharField(max_length=50)
    ship_to_name = models.CharField(max_length=100)
    ship_to_address = models.CharField(max_length=200)
    ship_to_city = models.CharField(max_length=100)
    ship_to_state = models.CharField(max_length=50)
    ship_to_zip = models.CharField(max_length=20)
    ship_to_country = models.CharField(max_length=50)
    carrier = models.CharField(max_length=100, blank=True, null=True)
    total_weight_lb = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    line_items = models.IntegerField()
    sku_quantity = models.JSONField()
    total_item_qty = models.IntegerField()
    volume_cuft = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    packages = models.IntegerField()
    status = models.CharField(max_length=50)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Order {self.transaction_id} for {self.customer.company_name}'