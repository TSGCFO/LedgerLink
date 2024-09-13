from django.shortcuts import render
from django.views import View
from .forms import BillingForm
from .services.billing_calculator import BillingCalculator
from django.http import HttpResponse
import csv
import json

class GenerateBillingView(View):
    template_name = 'billing/generate_billing.html'

    def get(self, request):
        form = BillingForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = BillingForm(request.POST)
        if form.is_valid():
            customer = form.cleaned_data['customer']
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']

            calculator = BillingCalculator(customer, start_date, end_date)
            billing_result = calculator.calculate_billing()

            return render(request, 'billing/billing_result.html', {'result': billing_result})
        return render(request, self.template_name, {'form': form})

class ExportBillingView(View):
    def get(self, request):
        # Assume we're storing the last billing result in the session
        billing_result = request.session.get('last_billing_result')
        if not billing_result:
            return HttpResponse("No billing data available for export.")

        export_format = request.GET.get('format', 'csv')

        if export_format == 'csv':
            return self.export_csv(billing_result)
        elif export_format == 'json':
            return self.export_json(billing_result)
        else:
            return HttpResponse("Unsupported export format.")

    def export_csv(self, billing_result):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="billing_export.csv"'

        writer = csv.writer(response)
        writer.writerow(['Customer', 'Start Date', 'End Date', 'Total Bill'])
        writer.writerow([
            billing_result['customer'],
            billing_result['start_date'],
            billing_result['end_date'],
            billing_result['total_bill']
        ])

        writer.writerow(['Order ID', 'Service', 'Cost'])
        for detail in billing_result['billing_details']:
            for service in detail['services']:
                writer.writerow([
                    detail['order']['transaction_id'],
                    service['service_name'],
                    service['cost']
                ])

        return response

    def export_json(self, billing_result):
        response = HttpResponse(content_type='application/json')
        response['Content-Disposition'] = 'attachment; filename="billing_export.json"'
        json.dump(billing_result, response, indent=2)
        return response