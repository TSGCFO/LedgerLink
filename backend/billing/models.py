from django.db import models
from django.utils import timezone

class Customer(models.Model):
    customer_id = models.AutoField(primary_key=True)
    company_name = models.CharField(max_length=100)
    legal_business_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    address = models.CharField(max_length=200, null=True, blank=True)
    city = models.CharField(max_length=50, null=True, blank=True)
    state = models.CharField(max_length=50, null=True, blank=True)
    zip = models.CharField(max_length=20, null=True, blank=True)
    country = models.CharField(max_length=50, null=True, blank=True)
    business_type = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Service(models.Model):
    service_id = models.AutoField(primary_key=True)
    service_name = models.CharField(max_length=100, unique=True)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class CustomerService(models.Model):
    customer_service_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('customer', 'service')
        indexes = [
            models.Index(fields=['customer'], name='idx_cust_svc_cust_id'),
            models.Index(fields=['service'], name='idx_cust_svc_svc_id')
        ]

class Insert(models.Model):
    insert_id = models.AutoField(primary_key=True)
    sku = models.CharField(max_length=100)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    insert_name = models.CharField(max_length=100)
    insert_quantity = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.CheckConstraint(check=models.Q(insert_quantity__gte=0), name='insert_quantity_check')
        ]
        indexes = [
            models.Index(fields=['sku', 'customer'], name='idx_ins_sku_cust_id')
        ]

class Product(models.Model):
    sku = models.CharField(max_length=100)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    labeling_unit_1 = models.CharField(max_length=50, null=True, blank=True)
    labeling_quantity_1 = models.PositiveIntegerField(null=True, blank=True)
    labeling_unit_2 = models.CharField(max_length=50, null=True, blank=True)
    labeling_quantity_2 = models.PositiveIntegerField(null=True, blank=True)
    labeling_unit_3 = models.CharField(max_length=50, null=True, blank=True)
    labeling_quantity_3 = models.PositiveIntegerField(null=True, blank=True)
    labeling_unit_4 = models.CharField(max_length=50, null=True, blank=True)
    labeling_quantity_4 = models.PositiveIntegerField(null=True, blank=True)
    labeling_unit_5 = models.CharField(max_length=50, null=True, blank=True)
    labeling_quantity_5 = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('sku', 'customer')
        constraints = [
            models.CheckConstraint(check=models.Q(labeling_quantity_1__gte=0), name='products_label_qty_1_check'),
            models.CheckConstraint(check=models.Q(labeling_quantity_2__gte=0), name='products_label_qty_2_check'),
            models.CheckConstraint(check=models.Q(labeling_quantity_3__gte=0), name='products_label_qty_3_check'),
            models.CheckConstraint(check=models.Q(labeling_quantity_4__gte=0), name='products_label_qty_4_check'),
            models.CheckConstraint(check=models.Q(labeling_quantity_5__gte=0), name='products_label_qty_5_check')
        ]
        indexes = [
            models.Index(fields=['customer'], name='idx_prod_cust_id')
        ]

class ServiceLog(models.Model):
    log_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    sku = models.CharField(max_length=100)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)
    performed_at = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.CheckConstraint(check=models.Q(quantity__gte=0), name='svc_logs_qty_check')
        ]
        indexes = [
            models.Index(fields=['customer'], name='idx_svc_logs_cust_id'),
            models.Index(fields=['service'], name='idx_svc_logs_svc_id'),
            models.Index(fields=['sku', 'customer'], name='idx_svc_logs_sku_cust_id')
        ]

class Order(models.Model):
    transaction_id = models.IntegerField(primary_key=True)
    create_date = models.DateTimeField()
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    customer_name = models.CharField(max_length=100)
    close_date = models.DateTimeField(null=True, blank=True)
    reference_number = models.CharField(max_length=50)
    ship_to_name = models.CharField(max_length=100)
    ship_to_company = models.CharField(max_length=100, null=True, blank=True)
    ship_to_address = models.CharField(max_length=200)
    ship_to_address2 = models.CharField(max_length=200, null=True, blank=True)
    ship_to_city = models.CharField(max_length=100)
    ship_to_state = models.CharField(max_length=50)
    ship_to_zip = models.CharField(max_length=20)
    ship_to_country = models.CharField(max_length=50)
    carrier = models.CharField(max_length=100, null=True, blank=True)
    total_weight_lb = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    line_items = models.IntegerField()
    sku_quantity = models.JSONField()
    total_item_qty = models.IntegerField()
    volume_cuft = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    packages = models.IntegerField()
    markfor_lists = models.TextField(null=True, blank=True)
    ship_service = models.CharField(max_length=100, null=True, blank=True)
    warehouse_instructions = models.TextField(null=True, blank=True)
    allocation_status = models.CharField(max_length=50, null=True, blank=True)
    asn_sent_date = models.DateTimeField(null=True, blank=True)
    batch_id = models.CharField(max_length=50, null=True, blank=True)
    batch_name = models.CharField(max_length=100, null=True, blank=True)
    bill_of_lading = models.CharField(max_length=100, null=True, blank=True)
    billing_type = models.CharField(max_length=50, null=True, blank=True)
    cancel_date = models.DateTimeField(null=True, blank=True)
    confirm_asn_sent_date = models.DateTimeField(null=True, blank=True)
    earliest_ship_date = models.DateTimeField(null=True, blank=True)
    end_of_day_request_date = models.DateTimeField(null=True, blank=True)
    load_number = models.CharField(max_length=50, null=True, blank=True)
    load_out_percent = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    load_out_date = models.DateTimeField(null=True, blank=True)
    markfor_name_id = models.CharField(max_length=100, null=True, blank=True)
    master_bill_of_lading = models.CharField(max_length=100, null=True, blank=True)
    pack_done_date = models.DateTimeField(null=True, blank=True)
    parcel_label_type = models.CharField(max_length=50, null=True, blank=True)
    pick_done_date = models.DateTimeField(null=True, blank=True)
    pick_job_assignee = models.CharField(max_length=50, null=True, blank=True)
    pick_job_id = models.CharField(max_length=50, null=True, blank=True)
    pick_ticket_print_date = models.DateTimeField(null=True, blank=True)
    pickup_date = models.DateTimeField(null=True, blank=True)
    purchase_order = models.CharField(max_length=100, null=True, blank=True)
    retailer_id = models.CharField(max_length=50, null=True, blank=True)
    ship_to_email = models.CharField(max_length=100, null=True, blank=True)
    ship_to_phone = models.CharField(max_length=20, null=True, blank=True)
    small_parcel_ship_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=50, null=True, blank=True)
    time_zone = models.CharField(max_length=50, null=True, blank=True)
    tracking_number = models.CharField(max_length=100, null=True, blank=True)
    volume_m3 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    warehouse = models.CharField(max_length=100, null=True, blank=True)
    total_weight_kg = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_by = models.CharField(max_length=50, null=True, blank=True)
    updated_by = models.CharField(max_length=50, null=True, blank=True)
    create_source = models.CharField(max_length=50, null=True, blank=True)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        constraints = [
            models.CheckConstraint(check=models.Q(line_items__gte=0), name='orders_line_items_check'),
            models.CheckConstraint(check=models.Q(load_out_percent__gte=0, load_out_percent__lte=100), name='orders_load_out_percent_check'),
            models.CheckConstraint(check=models.Q(packages__gte=0), name='orders_packages_check'),
            models.CheckConstraint(check=models.Q(total_item_qty__gte=0), name='orders_total_item_qty_check'),
            models.CheckConstraint(check=models.Q(total_weight_kg__gte=0), name='orders_total_weight_kg_check'),
            models.CheckConstraint(check=models.Q(total_weight_lb__gte=0), name='orders_total_weight_lb_check'),
            models.CheckConstraint(check=models.Q(volume_cuft__gte=0), name='orders_volume_cuft_check'),
            models.CheckConstraint(check=models.Q(volume_m3__gte=0), name='orders_volume_m3_check'),
        ]
        indexes = [
            models.Index(fields=['create_date'], name='idx_orders_create_date'),
            models.Index(fields=['customer'], name='idx_orders_customer_id'),
            models.Index(fields=['reference_number'], name='idx_orders_reference_number'),
            models.Index(fields=['status'], name='idx_orders_status'),
            models.Index(fields=['tracking_number'], name='idx_orders_tracking_number'),
            models.Index(fields=['transaction_id'], name='idx_orders_transaction_id'),
        ]
