from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy

class SuccessMessageMixin:
    """Add a success message on successful form submission."""
    success_message = ''

    def form_valid(self, form):
        response = super().form_valid(form)
        success_message = self.get_success_message(form.cleaned_data)
        if success_message:
            messages.success(self.request, success_message)
        return response

    def get_success_message(self, cleaned_data):
        return self.success_message % cleaned_data if self.success_message else ''

class OrderStatusMixin:
    """Add order status tracking functionality."""
    def track_status_change(self, old_status, new_status):
        if old_status != new_status:
            # Add status tracking logic here
            pass

class AuditTrailMixin:
    """Add audit trail for order changes."""
    def save_audit_trail(self, changes):
        # Add audit trail logic here
        pass