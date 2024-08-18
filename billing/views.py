from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.views.generic import ListView, DetailView, CreateView
from .models import Invoice, Charge
from .forms import InvoiceForm


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


class UninvoicedChargeListView(ListView):
    model = Charge
    template_name = 'billing/uninvoiced_charge_list.html'
    context_object_name = 'charges'

    def get_queryset(self):
        return Charge.objects.filter(invoiced=False)

class AddChargeToInvoiceView(View):
    def post(self, request, charge_id):
        charge = Charge.objects.get(id=charge_id)
        invoice_id = request.POST.get('invoice_id')
        invoice = Invoice.objects.get(id=invoice_id)
        charge.invoice = invoice
        charge.invoiced = True
        charge.save()
        return redirect('uninvoiced_charge_list')

class InvoiceCreateView(CreateView):
    model = Invoice
    form_class = InvoiceForm
    template_name = 'billing/invoice_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['uninvoiced_charges'] = Charge.objects.filter(invoiced=False)
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        charges_ids = self.request.POST.getlist('charges')
        for charge_id in charges_ids:
            charge = Charge.objects.get(id=charge_id)
            charge.invoice = self.object
            charge.invoiced = True
            charge.save()
        return response