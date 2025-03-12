from django.db import models
from django.utils import timezone
from customers.models import Customer
from orders.models import Order
from services.models import Service
import json
import logging

logger = logging.getLogger(__name__)


class BillingReport(models.Model):
    """
    Main model for storing billing report data.
    Contains information about a customer's billing for a specific date range.
    """
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='billing_reports_v2')
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    service_totals = models.JSONField(default=dict)
    metadata = models.JSONField(default=dict, blank=True, 
                              help_text="Additional metadata for the report (customer service selection, etc.)")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Billing Report"
        verbose_name_plural = "Billing Reports"
        
    def __str__(self):
        return f"Billing Report #{self.id} - {self.customer.company_name}"
        
    def update_total_amount(self):
        """Update the total amount based on service totals."""
        try:
            if not self.service_totals:
                self.total_amount = 0
                return
                
            # Sum all service amounts from service_totals
            total = sum(data['amount'] for data in self.service_totals.values())
            self.total_amount = total
            logger.info(f"Updated report #{self.id} total_amount to {total} based on service totals")
            
            # Force save to ensure the total_amount is persisted
            from django.db import connection
            if connection.in_atomic_block:
                # We're in a transaction, just save normally
                self.save(update_fields=['total_amount'])
            else:
                # Use a separate transaction
                from django.db import transaction
                with transaction.atomic():
                    self.save(update_fields=['total_amount'])
            
        except Exception as e:
            logger.error(f"Error updating total amount: {str(e)}")
            # Fallback to calculating from order costs
            try:
                from django.db.models import Sum
                total = self.order_costs.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
                self.total_amount = total
                logger.info(f"Fallback: Updated report #{self.id} total_amount to {total} based on order costs")
                
                # Force save the fallback value
                try:
                    from django.db import transaction
                    with transaction.atomic():
                        self.save(update_fields=['total_amount'])
                except Exception as save_e:
                    logger.error(f"Error saving fallback total: {str(save_e)}")
                    
            except Exception as inner_e:
                logger.error(f"Fallback failed: {str(inner_e)}")
        
    def add_order_cost(self, order_cost):
        """
        Add an order cost to this report and update totals.
        
        Args:
            order_cost: OrderCost object to add
        """
        # Update service totals
        for service_cost in order_cost.service_costs.all():
            service_id = str(service_cost.service_id)
            if service_id in self.service_totals:
                self.service_totals[service_id]['amount'] += float(service_cost.amount)
            else:
                self.service_totals[service_id] = {
                    'service_name': service_cost.service_name,
                    'amount': float(service_cost.amount)
                }
        
        # Save the updated service_totals first
        from django.db import transaction
        with transaction.atomic():
            self.save(update_fields=['service_totals'])
            
        # Update total amount from service totals - this will also save
        self.update_total_amount()
    
    def to_dict(self):
        """
        Convert report to dictionary format.
        
        Returns:
            Dictionary representation of the report
        """
        # Ensure total_amount is correct before returning
        if self.service_totals:
            # Double-check the total amount matches service_totals
            calculated_total = sum(data['amount'] for data in self.service_totals.values())
            if abs(float(self.total_amount) - calculated_total) > 0.01:  # Allow for small decimal differences
                logger.warning(f"Total amount discrepancy detected: DB={self.total_amount}, calculated={calculated_total}")
                # Update the total_amount to match service_totals
                self.total_amount = calculated_total
                try:
                    from django.db import transaction
                    with transaction.atomic():
                        self.save(update_fields=['total_amount'])
                except Exception as e:
                    logger.error(f"Error saving corrected total amount: {str(e)}")
                    
        return {
            'id': self.id,
            'customer_id': self.customer.id,
            'customer_name': self.customer.company_name,
            'start_date': self.start_date.strftime('%Y-%m-%d'),
            'end_date': self.end_date.strftime('%Y-%m-%d'),
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'orders': [order_cost.to_dict() for order_cost in self.order_costs.all()],
            'service_totals': self.service_totals,
            'total_amount': float(self.total_amount),
            'metadata': self.metadata
        }
    
    def to_json(self):
        """
        Convert report to JSON format.
        
        Returns:
            JSON string representation of the report
        """
        return json.dumps(self.to_dict())


class OrderCost(models.Model):
    """
    Represents the cost details for a specific order within a billing report.
    Links an order to a billing report and contains service costs.
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_costs_v2')
    billing_report = models.ForeignKey(BillingReport, on_delete=models.CASCADE, related_name='order_costs')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    class Meta:
        verbose_name = "Order Cost"
        verbose_name_plural = "Order Costs"
    
    def __str__(self):
        return f"Order Cost #{self.id} - Order #{self.order.id}"
    
    def add_service_cost(self, service_cost):
        """
        Add a service cost to this order and update total.
        
        Args:
            service_cost: ServiceCost object to add
        """
        self.total_amount += service_cost.amount
        self.save()
    
    def to_dict(self):
        """
        Convert order cost to dictionary format.
        
        Returns:
            Dictionary representation of the order cost
        """
        return {
            'order_id': self.order.id,
            'reference_number': self.order.reference_number,
            'order_date': self.order.created_at.strftime('%Y-%m-%d'),
            'service_costs': [sc.to_dict() for sc in self.service_costs.all()],
            'total_amount': float(self.total_amount)
        }


class ServiceCost(models.Model):
    """
    Represents the cost of a specific service applied to an order.
    Contains service details and the calculated amount.
    """
    order_cost = models.ForeignKey(OrderCost, on_delete=models.CASCADE, related_name='service_costs')
    service_id = models.IntegerField()
    service_name = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        verbose_name = "Service Cost"
        verbose_name_plural = "Service Costs"
    
    def __str__(self):
        return f"{self.service_name} - ${self.amount}"
    
    def to_dict(self):
        """
        Convert service cost to dictionary format.
        
        Returns:
            Dictionary representation of the service cost
        """
        return {
            'service_id': self.service_id,
            'service_name': self.service_name,
            'amount': float(self.amount)
        }