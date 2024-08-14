from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from .models import Invoice, Charge


# ListView for Invoices
class InvoiceListView(ListView):
    model = Invoice
    template_name = 'billing/invoice_list.html'
    context_object_name = 'invoices'

    def get_queryset(self):
        # Optionally filter invoices by customer
        customer_id = self.request.GET.get('customer_id')
        if customer_id:
            return Invoice.objects.filter(customer_id=customer_id)
        return Invoice.objects.all()


class InvoiceDetailView(DetailView):
    model = Invoice
    template_name = 'billing/invoice_detail.html'
    context_object_name = 'invoice'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['charges'] = self.object.charges.all()
        return context


# Optional: DetailView for a specific Charge
class ChargeDetailView(DetailView):
    model = Charge
    template_name = 'billing/charge_detail.html'
    context_object_name = 'charge'