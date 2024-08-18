from django.db import models
from orders.models import Order
from customer_services.models import CustomerService
from customers.models import Customer  # Correct import of the Customer model

class Invoice(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)  # Links to the Customer model
    order = models.ForeignKey(Order, on_delete=models.CASCADE)  # Links to the Order model
    invoice_date = models.DateTimeField(auto_now_add=True)  # Automatically sets the date of invoice creation
    due_date = models.DateTimeField(blank=True, null=True)  # Optional due date for the invoice
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)  # Total amount on the invoice
    currency = models.CharField(max_length=3, choices=[('USD', 'US Dollar'), ('CAD', 'Canadian Dollar')])  # Currency of the invoice
    status = models.CharField(max_length=20, default='Generated')  # Status of the invoice

    def __str__(self):
        # Returns a string representation showing the invoice ID, customer name, and order transaction ID
        return f"Invoice {self.id} for {self.customer.company_name} - Order {self.order.transaction_id}"

class Charge(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='charges', blank=True, null=True)  # Links to the Invoice model
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='charges')  # Links to the Order model
    service = models.ForeignKey(CustomerService, on_delete=models.CASCADE)  # Links to the CustomerService model
    transaction_id = models.IntegerField()  # Order's transaction ID
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)  # Links to the Customer model
    close_date = models.DateTimeField(blank=True, null=True)  # Close date of the order
    reference_number = models.CharField(max_length=100)  # Reference number of the order
    ship_to_name = models.CharField(max_length=100, blank=True, null=True)  # Shipping name
    ship_to_company = models.CharField(max_length=100, blank=True, null=True)  # Shipping company name
    ship_to_address = models.CharField(max_length=200, blank=True, null=True)  # Shipping address
    ship_to_address2 = models.CharField(max_length=200, blank=True, null=True)  # Shipping address (additional line)
    ship_to_city = models.CharField(max_length=100, blank=True, null=True)  # Shipping city
    ship_to_state = models.CharField(max_length=50, blank=True, null=True)  # Shipping state
    ship_to_zip = models.CharField(max_length=20, blank=True, null=True)  # Shipping postal code
    ship_to_country = models.CharField(max_length=50, blank=True, null=True)  # Shipping country
    weight_lb = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)  # Weight of the shipment
    line_items = models.IntegerField(blank=True, null=True)  # Number of line items in the order
    sku_quantity = models.JSONField(blank=True, null=True)  # Quantity of SKUs
    total_item_qty = models.IntegerField(blank=True, null=True)  # Total item quantity
    volume_cuft = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)  # Volume in cubic feet
    packages = models.IntegerField(blank=True, null=True)  # Number of packages
    notes = models.TextField(blank=True, null=True)  # Additional notes
    carrier = models.CharField(max_length=50, blank=True, null=True)  # Carrier information
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # Charge amount for this service
    currency = models.CharField(max_length=3, choices=[('USD', 'US Dollar'), ('CAD', 'Canadian Dollar')])  # Currency of the charge
    invoiced = models.BooleanField(default=False)  # New field to track if the charge is invoiced

    def __str__(self):
        # Returns a string representation showing the customer name, order transaction ID, and service name
        return f"Charge for {self.customer.company_name} - Order {self.order.transaction_id} - Service: {self.service.service.service_name}"

    @property
    def total_for_service(self):
        # Currently, this returns the charge amount, but can be extended for more complex calculations
        return self.amount
