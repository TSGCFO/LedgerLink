# billing/views.py

from django.shortcuts import render, get_object_or_404, redirect
from customers.models import Customer
from orders.models import Order
from .services.billing_calculator import BillingCalculator
from .services.invoice_generator import InvoiceGenerator
from .services.report_exporter import ReportExporter
from .forms import BillingForm
from .models import Invoice


def generate_billing_view(request):
    customer = None
    start_date = None
    end_date = None
    orders_queryset = Order.objects.none()

    if request.method == "POST":
        form = BillingForm(request.POST)
        if form.is_valid():
            customer = form.cleaned_data["customer"]
            start_date = form.cleaned_data["start_date"]
            end_date = form.cleaned_data["end_date"]
            orders_queryset = Order.objects.filter(customer=customer)
            if start_date and end_date:
                orders_queryset = orders_queryset.filter(order_date__range=(start_date, end_date))
            form = BillingForm(customer=customer, start_date=start_date, end_date=end_date)
            form.fields['orders'].queryset = orders_queryset
            # Return the rendered template with the updated form
            return render(request, "billing/generate_billing.html", {"form": form})
    else:
        form = BillingForm()

    return render(request, "billing/generate_billing.html", {"form": form})


def invoice_detail_view(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    return render(request, "billing/invoice_detail.html", {"invoice": invoice})


def invoice_list_view(request):
    invoices = Invoice.objects.all()
    return render(request, "billing/invoice_list.html", {"invoices": invoices})


def export_report_view(request):
    report_exporter = ReportExporter()
    if request.GET.get("format") == "pdf":
        pdf_file = report_exporter.export_to_pdf(report_data={})
        return pdf_file  # Assumes `report_data` is provided as needed
    elif request.GET.get("format") == "excel":
        excel_file = report_exporter.export_to_excel(report_data={})
        return excel_file  # Assumes `report_data` is provided as needed

    return redirect("invoice_list")  # Fallback if no format is provided
