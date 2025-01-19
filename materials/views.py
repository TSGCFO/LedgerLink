from idlelib.query import Query

from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Material, BoxPrice
from .forms import MaterialForm, BoxPriceForm

# Create your views here.


class MaterialListView(ListView):
    model = Material
    template_name = 'materials/material_list.html'
    context_object_name = 'materials'

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('search', '')
        sort_by = self.request.GET.get('sort', '')

        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query)
            )

        # Sorting functionality
        if sort_by in ['name', 'unit_price']:
            queryset = queryset.order_by(sort_by)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        context['sort'] = self.request.GET.get('sort', '')
        return context


class MaterialDetailView(DetailView):
    model = Material
    template_name = 'materials/material_detail.html'
    context_object_name = 'material'


class MaterialCreateView(CreateView):
    model = Material
    form_class = MaterialForm
    template_name = 'materials/material_form.html'
    success_url = reverse_lazy('materials:material_list')


class MaterialUpdateView(UpdateView):
    model = Material
    form_class = MaterialForm
    template_name = 'materials/material_form.html'
    success_url = reverse_lazy('materials:material_list')


class MaterialDeleteView(DeleteView):
    model = Material
    template_name = 'materials/material_confirm_delete.html'
    success_url = reverse_lazy('materials:material_list')


class BoxPriceListView(ListView):
    model = BoxPrice
    template_name = 'materials/boxprice_list.html'
    context_object_name = 'boxprices'

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('search', '')
        sort_by = self.request.GET.get('sort', '')

        # Search functionality
        if search_query:
            queryset = queryset.filter(
                Q(box_type__icontains=search_query)
            )

        # Sorting functionality
        if sort_by in ['box_type', 'price']:
            queryset = queryset.order_by(sort_by)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        context['sort'] = self.request.GET.get('sort', '')
        return context


class BoxPriceDetailView(DetailView):
    model = BoxPrice
    template_name = 'materials/boxprice_detail.html'
    context_object_name = 'boxprice'


class BoxPriceCreateView(CreateView):
    model = BoxPrice
    form_class = BoxPriceForm
    template_name = 'materials/boxprice_form.html'
    success_url = reverse_lazy('boxprice_list')


class BoxPriceUpdateView(UpdateView):
    model = BoxPrice
    form_class = BoxPriceForm
    template_name = 'materials/boxprice_form.html'
    success_url = reverse_lazy('boxprice_list')


class BoxPriceDeleteView(DeleteView):
    model = BoxPrice
    template_name = 'materials/boxprice_confirm_delete.html'
    success_url = reverse_lazy('boxprice_list')
