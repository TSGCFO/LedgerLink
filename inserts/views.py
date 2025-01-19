from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Insert
from .forms import InsertForm
from django.http import Http404



# Create your views here.

class InsertListView(ListView):
    model = Insert
    template_name = 'inserts/insert_list.html'
    context_object_name = 'inserts'


class InsertDetailView(DetailView):
    model = Insert
    template_name = 'inserts/insert_detail.html'
    context_object_name = 'insert'


class InsertCreateView(CreateView):
    model = Insert
    form_class = InsertForm
    template_name = 'inserts/insert_form.html'
    success_url = reverse_lazy('insert_list')


class InsertUpdateView(UpdateView):
    model = Insert
    form_class = InsertForm
    template_name = 'inserts/insert_form.html'
    success_url = reverse_lazy('insert_list')


class InsertDeleteView(DeleteView):
    model = Insert
    template_name = 'inserts/insert_confirm_delete.html'
    success_url = reverse_lazy('insert_list')

from django.http import Http404

class SkuDetailView(DetailView):
    model = Insert
    template_name = 'products/product_detail.html'  # Use the provided template
    context_object_name = 'product'

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        sku = self.kwargs.get('sku')
        try:
            return queryset.get(sku=sku)
        except self.model.DoesNotExist:
            raise Http404("SKU not found")
