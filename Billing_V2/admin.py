from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import BillingReport, OrderCost, ServiceCost


class ServiceCostInline(admin.TabularInline):
    """Inline admin for ServiceCost"""
    model = ServiceCost
    extra = 0
    readonly_fields = ['service_id', 'service_name', 'amount']
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False


class OrderCostInline(admin.TabularInline):
    """Inline admin for OrderCost"""
    model = OrderCost
    extra = 0
    readonly_fields = ['order', 'order_link', 'total_amount']
    fields = ['order', 'order_link', 'total_amount']
    show_change_link = True
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False
        
    def order_link(self, obj):
        """Generate a link to the order in the admin"""
        if obj and obj.order:
            url = reverse('admin:orders_order_change', args=[obj.order.transaction_id])
            return format_html('<a href="{}">View Order</a>', url)
        return "-"
    order_link.short_description = "Order Link"


@admin.register(OrderCost)
class OrderCostAdmin(admin.ModelAdmin):
    """Admin for OrderCost model"""
    list_display = ['id', 'order_id', 'order_reference', 'billing_report_link', 'total_amount']
    search_fields = ['order__reference_number', 'order__transaction_id', 'billing_report__id']
    readonly_fields = ['total_amount', 'order_link', 'billing_report_link']
    fields = ['order', 'order_link', 'billing_report', 'billing_report_link', 'total_amount']
    inlines = [ServiceCostInline]
    
    def order_reference(self, obj):
        """Get order reference number for display"""
        return obj.order.reference_number if obj.order else "-"
    order_reference.short_description = "Reference"
    
    def order_id(self, obj):
        """Get order ID for display"""
        return obj.order.transaction_id if obj.order else "-"
    order_id.short_description = "Order ID"
    
    def order_link(self, obj):
        """Generate a link to the order in the admin"""
        if obj and obj.order:
            url = reverse('admin:orders_order_change', args=[obj.order.transaction_id])
            return format_html('<a href="{}">View Order</a>', url)
        return "-"
    order_link.short_description = "Order Link"
    
    def billing_report_link(self, obj):
        """Generate a link to the billing report in the admin"""
        if obj and obj.billing_report:
            url = reverse('admin:Billing_V2_billingreport_change', args=[obj.billing_report.id])
            return format_html('<a href="{}">View Report</a>', url)
        return "-"
    billing_report_link.short_description = "Report Link"
    
    def has_add_permission(self, request):
        return False


@admin.register(BillingReport)
class BillingReportAdmin(admin.ModelAdmin):
    """Admin for BillingReport model"""
    list_display = ['id', 'customer_name', 'start_date', 'end_date', 'formatted_total', 
                   'order_count', 'created_at']
    list_filter = ['customer', 'created_at']
    search_fields = ['customer__company_name', 'id']
    readonly_fields = ['total_amount', 'service_totals', 'customer_link', 'formatted_json']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    inlines = [OrderCostInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('customer', 'customer_link', 'start_date', 'end_date', 'total_amount')
        }),
        ('Service Totals', {
            'fields': ('formatted_json',),
            'classes': ('collapse',),
        }),
    )
    
    def customer_name(self, obj):
        """Get customer name for display"""
        return obj.customer.company_name if obj.customer else "-"
    customer_name.short_description = "Customer"
    
    def formatted_total(self, obj):
        """Format total amount as currency"""
        return f"${obj.total_amount:,.2f}" if obj.total_amount else "$0.00"
    formatted_total.short_description = "Total Amount"
    
    def order_count(self, obj):
        """Get count of orders for display"""
        return obj.order_costs.count()
    order_count.short_description = "Orders"
    
    def customer_link(self, obj):
        """Generate a link to the customer in the admin"""
        if obj and obj.customer:
            url = reverse('admin:customers_customer_change', args=[obj.customer.id])
            return format_html('<a href="{}">View Customer</a>', url)
        return "-"
    customer_link.short_description = "Customer Link"
    
    def formatted_json(self, obj):
        """Format service totals JSON for display"""
        import json
        from django.utils.safestring import mark_safe
        
        if not obj.service_totals:
            return mark_safe("<pre>No service totals</pre>")
            
        # Format the JSON with indentation
        formatted = json.dumps(obj.service_totals, indent=4)
        
        # Format as HTML with syntax highlighting
        return mark_safe(f'<pre style="background-color: #f8f8f8; padding: 10px; '
                        f'border: 1px solid #ddd; border-radius: 4px;">{formatted}</pre>')
    formatted_json.short_description = "Service Totals"
    
    def has_add_permission(self, request):
        """Disable adding reports directly through admin"""
        return False


# Register ServiceCost model separately if needed
# admin.site.register(ServiceCost)