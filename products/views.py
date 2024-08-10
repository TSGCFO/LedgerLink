# products/views.py
import pandas as pd
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, View
from .models import Product
from .forms import ProductForm, ProductUploadForm
from customers.models import Customer
from django.db.models import Q


class ProductListView(ListView):
    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'products'

    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            return Product.objects.filter(
                Q(sku__icontains=query) |
                Q(labeling_unit_1__icontains=query) |
                Q(labeling_unit_2__icontains=query) |
                Q(labeling_unit_3__icontains=query) |
                Q(labeling_unit_4__icontains=query) |
                Q(labeling_unit_5__icontains=query)
            )
        return Product.objects.all()


class ProductDetailView(DetailView):
    model = Product
    template_name = 'products/product_detail.html'
    context_object_name = 'product'


class ProductCreateView(CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'products/product_form.html'
    success_url = reverse_lazy('product_list')


class ProductUpdateView(UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'products/product_form.html'
    success_url = reverse_lazy('product_list')


class ProductUploadView(View):
    form_class = ProductUploadForm
    template_name = 'products/product_upload.html'

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            try:
                if file.name.endswith('.csv'):
                    data = pd.read_csv(file)
                elif file.name.endswith('.xlsx'):
                    data = pd.read_excel(file)
                else:
                    raise ValueError('Unsupported file type')

                # Process data
                for _, row in data.iterrows():
                    product, created = Product.objects.update_or_create(
                        sku=row['sku'],
                        defaults={
                            'labeling_unit_1': row.get('labeling_unit_1', ''),
                            'labeling_quantity_1': row.get('labeling_quantity_1', 0),
                            'labeling_unit_2': row.get('labeling_unit_2', ''),
                            'labeling_quantity_2': row.get('labeling_quantity_2', 0),
                            'labeling_unit_3': row.get('labeling_unit_3', ''),
                            'labeling_quantity_3': row.get('labeling_quantity_3', 0),
                            'labeling_unit_4': row.get('labeling_unit_4', ''),
                            'labeling_quantity_4': row.get('labeling_quantity_4', 0),
                            'labeling_unit_5': row.get('labeling_unit_5', ''),
                            'labeling_quantity_5': row.get('labeling_quantity_5', 0),
                            'customer': Customer.objects.get(id=row['customer_id']),
                        }
                    )
            except Exception as e:
                return render(request, self.template_name, {'form': form, 'error': str(e)})

            return redirect('product_list')
        return render(request, self.template_name, {'form': form})
