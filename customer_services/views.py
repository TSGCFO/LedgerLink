from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import CustomerService
from .forms import CustomerServiceForm


# Create your views here.

class CustomerServiceListView(ListView):
    model = CustomerService
    template_name = 'customer_services/customer_service_list.html'
    context_object_name = 'customer_services'


class CustomerServiceDetailView(DetailView):
    model = CustomerService
    template_name = 'customer_services/customer_service_detail.html'
    context_object_name = 'customer_service'


class CustomerServiceCreateView(CreateView):
    model = CustomerService
    form_class = CustomerServiceForm
    template_name = 'customer_services/customer_service_form.html'
    success_url = reverse_lazy('customer_service_list')


class CustomerServiceUpdateView(UpdateView):
    model = CustomerService
    form_class = CustomerServiceForm
    template_name = 'customer_services/customer_service_form.html'
    success_url = reverse_lazy('customer_service_list')


class CustomerServiceDeleteView(DeleteView):
    model = CustomerService
    template_name = 'customer_services/customer_service_confirm_delete.html'
    success_url = reverse_lazy('customer_service_list')
