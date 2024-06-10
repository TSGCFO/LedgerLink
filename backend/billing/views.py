from rest_framework import viewsets
from rest_framework.views import APIView  # Import APIView
from rest_framework.response import Response  # Import Response
from rest_framework import status  # Import status
from .models import Customer, Service, CustomerService, Insert, Product, ServiceLog, Order
from .serializers import CustomerSerializer, ServiceSerializer, CustomerServiceSerializer, InsertSerializer, ProductSerializer, ServiceLogSerializer, OrdersSerializer
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import ProductUploadForm
import pandas as pd

class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer

class CustomerServiceViewSet(viewsets.ModelViewSet):
    queryset = CustomerService.objects.all()
    serializer_class = CustomerServiceSerializer

class InsertViewSet(viewsets.ModelViewSet):
    queryset = Insert.objects.all()
    serializer_class = InsertSerializer

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class ServiceLogViewSet(viewsets.ModelViewSet):
    queryset = ServiceLog.objects.all()
    serializer_class = ServiceLogSerializer

class OrdersViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrdersSerializer

class OrderImportView(APIView):  # Add this class
    def post(self, request, format=None):
        serializer = OrdersSerializer(data=request.data, many=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"status": "success", "data": serializer.data}, status=status.HTTP_201_CREATED)
        return Response({"status": "error", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


# New views for file upload and export

def upload_file(request):
    if request.method == 'POST':
        form = ProductUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            df = pd.read_excel(file) if file.name.endswith('.xlsx') else pd.read_csv(file)

            for _, row in df.iterrows():
                Product.objects.create(
                    sku=row['SKU'],
                    customer_id=row['Customer ID'],
                    labeling_unit_1=row.get('Labeling Unit 1', ''),
                    labeling_quantity_1=int(row.get('Labeling Quantity 1', 0) or 0),
                    labeling_unit_2=row.get('Labeling Unit 2', ''),
                    labeling_quantity_2=int(row.get('Labeling Quantity 2', 0) or 0),
                    labeling_unit_3=row.get('Labeling Unit 3', ''),
                    labeling_quantity_3=int(row.get('Labeling Quantity 3', 0) or 0),
                    labeling_unit_4=row.get('Labeling Unit 4', ''),
                    labeling_quantity_4=int(row.get('Labeling Quantity 4', 0) or 0),
                    labeling_unit_5=row.get('Labeling Unit 5', ''),
                    labeling_quantity_5=int(row.get('Labeling Quantity 5', 0) or 0),
                )
            return redirect('product_list')
    else:
        form = ProductUploadForm()
    return render(request, 'upload.html', {'form': form})

def download_template(request):
    columns = ['SKU', 'Customer ID', 'Labeling Unit 1', 'Labeling Quantity 1', 
               'Labeling Unit 2', 'Labeling Quantity 2', 'Labeling Unit 3', 
               'Labeling Quantity 3', 'Labeling Unit 4', 'Labeling Quantity 4', 
               'Labeling Unit 5', 'Labeling Quantity 5']
    df = pd.DataFrame(columns=columns)
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=product_template.xlsx'
    df.to_excel(response, index=False)
    return response

def export_products(request):
    products = Product.objects.all().values()
    df = pd.DataFrame(products)
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=products.xlsx'
    df.to_excel(response, index=False)
    return response

def product_list(request):
    products = Product.objects.all()
    return render(request, 'product_list.html', {'products': products})

def home(request):
    return render(request, 'home.html')
