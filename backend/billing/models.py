from django.db import models
from django.utils import timezone

class Customer(models.Model):
    customer_id = models.AutoField(primary_key=True)
    company_name = models.CharField(max_length=100)
    legal_business_name = models.CharField(max_length=100)
    email = models.EmailField(max_length=254, unique=True, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.CharField(max_length=200, blank=True, null=True)
    city = models.CharField(max_length=50, blank=True, null=True)
    state = models.CharField(max_length=50, blank=True, null=True)
    zip = models.CharField(max_length=20, blank=True, null=True)
    country = models.CharField(max_length=50, blank=True, null=True)
    business_type = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.company_name

    class Meta:
        indexes = [
            models.Index(fields=['email'], name='billing_customer_email_idx')
        ]
        unique_together = ('email',)


class Service(models.Model):
    service_id = models.AutoField(primary_key=True)
    service_name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['service_name'], name='billing_service_service_name_key'),
        ]
        indexes = [
            models.Index(fields=['service_name'], name='billing_svc_name_idx'),
        ]

    def __str__(self):
        return self.service_name

class CustomerService(models.Model):
    customer_service_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE)
    service = models.ForeignKey('Service', on_delete=models.CASCADE)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['customer', 'service'], name='customer_service_cust_serv_key'),
        ]
        indexes = [
            models.Index(fields=['customer'], name='cust_serv_cust_id_idx'),
            models.Index(fields=['service'], name='cust_serv_serv_id_idx'),
        ]

    def __str__(self):
        return f'{self.customer.company_name} - {self.service.service_name}'

class Insert(models.Model):
    insert_id = models.AutoField(primary_key=True)
    sku = models.CharField(max_length=100)
    insert_name = models.CharField(max_length=100)
    insert_quantity = models.IntegerField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.CheckConstraint(check=models.Q(insert_quantity__gte=0), name='insert_qty_check'),
        ]
        indexes = [
            models.Index(fields=['customer'], name='ins_cust_id_idx'),
            models.Index(fields=['sku', 'customer'], name='ins_sku_cust_idx'),
        ]

    def __str__(self):
        return self.insert_name

class Product(models.Model):
    id = models.BigAutoField(primary_key=True)
    sku = models.CharField(max_length=100)
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
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['sku', 'customer'], name='billing_product_sku_customer_id_uniq'),
            models.CheckConstraint(check=models.Q(labeling_quantity_1__gte=0), name='billing_product_labeling_quantity_1_check'),
            models.CheckConstraint(check=models.Q(labeling_quantity_2__gte=0), name='billing_product_labeling_quantity_2_check'),
            models.CheckConstraint(check=models.Q(labeling_quantity_3__gte=0), name='billing_product_labeling_quantity_3_check'),
            models.CheckConstraint(check=models.Q(labeling_quantity_4__gte=0), name='billing_product_labeling_quantity_4_check'),
            models.CheckConstraint(check=models.Q(labeling_quantity_5__gte=0), name='billing_product_labeling_quantity_5_check')
        ]
        indexes = [
            models.Index(fields=['customer'], name='product_cust_id_idx'),
        ]

    def __str__(self):
        return f'{self.sku} - {self.customer_id}'

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
    create_date = models.DateTimeField(default=timezone.now)
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE)  # ForeignKey field for Customer
    close_date = models.DateTimeField(blank=True, null=True)
    reference_number = models.CharField(max_length=50)
    ship_to_name = models.CharField(max_length=100)
    ship_to_company = models.CharField(max_length=100, blank=True, null=True)
    ship_to_address = models.CharField(max_length=200)
    ship_to_address2 = models.CharField(max_length=200, blank=True, null=True)
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
    markfor_lists = models.TextField(blank=True, null=True)
    ship_service = models.CharField(max_length=100, blank=True, null=True)
    warehouse_instructions = models.TextField(blank=True, null=True)
    allocation_status = models.CharField(max_length=50, blank=True, null=True)
    asn_sent_date = models.DateTimeField(blank=True, null=True)
    batch_id = models.CharField(max_length=50, blank=True, null=True)
    batch_name = models.CharField(max_length=100, blank=True, null=True)
    bill_of_lading = models.CharField(max_length=100, blank=True, null=True)
    billing_type = models.CharField(max_length=50, blank=True, null=True)
    cancel_date = models.DateTimeField(blank=True, null=True)
    confirm_asn_sent_date = models.DateTimeField(blank=True, null=True)
    earliest_ship_date = models.DateTimeField(blank=True, null=True)
    end_of_day_request_date = models.DateTimeField(blank=True, null=True)
    load_number = models.CharField(max_length=50, blank=True, null=True)
    load_out_percent = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    load_out_date = models.DateTimeField(blank=True, null=True)
    markfor_name_id = models.CharField(max_length=100, blank=True, null=True)
    master_bill_of_lading = models.CharField(max_length=100, blank=True, null=True)
    pack_done_date = models.DateTimeField(blank=True, null=True)
    parcel_label_type = models.CharField(max_length=50, blank=True, null=True)
    pick_done_date = models.DateTimeField(blank=True, null=True)
    pick_job_assignee = models.CharField(max_length=50, blank=True, null=True)
    pick_job_id = models.CharField(max_length=50, blank=True, null=True)
    pick_ticket_print_date = models.DateTimeField(blank=True, null=True)
    pickup_date = models.DateTimeField(blank=True, null=True)
    purchase_order = models.CharField(max_length=100, blank=True, null=True)
    retailer_id = models.CharField(max_length=50, blank=True, null=True)
    ship_to_email = models.CharField(max_length=100, blank=True, null=True)
    ship_to_phone = models.CharField(max_length=20, blank=True, null=True)
    small_parcel_ship_date = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=50, blank=True, null=True)
    time_zone = models.CharField(max_length=50, blank=True, null=True)
    tracking_number = models.CharField(max_length=100, blank=True, null=True)
    volume_m3 = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    warehouse = models.CharField(max_length=100, blank=True, null=True)
    total_weight_kg = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    created_by = models.CharField(max_length=50, blank=True, null=True)
    updated_by = models.CharField(max_length=50, blank=True, null=True)
    create_source = models.CharField(max_length=50, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Order {self.transaction_id} for {self.customer.company_name}'

    class Meta:
        constraints = [
            models.CheckConstraint(check=models.Q(line_items__gte=0), name='orders_line_items_check'),
            models.CheckConstraint(check=models.Q(load_out_percent__gte=0) & models.Q(load_out_percent__lte=100), name='orders_load_out_percent_check'),
            models.CheckConstraint(check=models.Q(packages__gte=0), name='orders_packages_check'),
            models.CheckConstraint(check=models.Q(total_item_qty__gte=0), name='orders_total_item_qty_check'),
            models.CheckConstraint(check=models.Q(total_weight_kg__gte=0), name='orders_total_weight_kg_check'),
            models.CheckConstraint(check=models.Q(total_weight_lb__gte=0), name='orders_total_weight_lb_check'),
            models.CheckConstraint(check=models.Q(volume_cuft__gte=0), name='orders_volume_cuft_check'),
            models.CheckConstraint(check=models.Q(volume_m3__gte=0), name='orders_volume_m3_check'),
        ]
        indexes = [
            models.Index(fields=['customer'], name='order_cust_id_idx'),
            models.Index(fields=['create_date'], name='orders_create_date_idx'),
            models.Index(fields=['reference_number'], name='orders_ref_num_idx'),
            models.Index(fields=['status'], name='orders_status_idx'),
            models.Index(fields=['tracking_number'], name='orders_track_num_idx'),
            models.Index(fields=['transaction_id'], name='orders_trans_id_idx'),
        ]

class Material(models.Model):
    material_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name


class Box(models.Model):
    box_id = models.AutoField(primary_key=True)
    length = models.DecimalField(max_digits=5, decimal_places=2)
    width = models.DecimalField(max_digits=5, decimal_places=2)
    height = models.DecimalField(max_digits=5, decimal_places=2)
    volume = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    prices = models.JSONField()  # Use django.db.models.JSONField

    def save(self, *args, **kwargs):
        self.volume = self.length * self.width * self.height
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.length}x{self.width}x{self.height}'

    class Meta:
        indexes = [
            models.Index(fields=['length', 'width', 'height']),
        ]
        constraints = [
            models.CheckConstraint(check=models.Q(length__gt=0), name='length_gt_0'),
            models.CheckConstraint(check=models.Q(width__gt=0), name='width_gt_0'),
            models.CheckConstraint(check=models.Q(height__gt=0), name='height_gt_0'),
        ]


class BoxPrice(models.Model):
    box = models.ForeignKey(Box, on_delete=models.CASCADE, related_name='box_prices')
    test_type = models.CharField(max_length=50)  # 200LB or ECT32
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'{self.box} - {self.test_type}: ${self.price}'

    class Meta:
        unique_together = ('box', 'test_type')
        indexes = [
            models.Index(fields=['box', 'test_type']),
        ]
        constraints = [
            models.CheckConstraint(check=models.Q(price__gte=0), name='price_gte_0'),
        ]
