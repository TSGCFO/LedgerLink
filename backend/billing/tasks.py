# billing/tasks.py

from azure.storage.blob import BlobServiceClient
import json
from celery import shared_task
from django.conf import settings
from .models import Order
from .serializers import OrdersSerializer

# Initialize the BlobServiceClient
blob_service_client = BlobServiceClient(
    account_url=f"https://{settings.AZURE_STORAGE_ACCOUNT_NAME}.blob.core.windows.net",
    credential=settings.AZURE_STORAGE_ACCOUNT_KEY
)

@shared_task
def check_blob_for_orders():
    container_client = blob_service_client.get_container_client(settings.AZURE_CONTAINER_NAME)
    blob_list = container_client.list_blobs()
    for blob in blob_list:
        blob_client = container_client.get_blob_client(blob)
        blob_data = blob_client.download_blob().readall().decode('utf-8')
        order_data = json.loads(blob_data)
        
        serializer = OrdersSerializer(data=order_data, many=True)
        if serializer.is_valid():
            serializer.save()
            print(f"Successfully imported orders from {blob.name}")
            blob_client.delete_blob()
        else:
            print(f"Error importing orders from {blob.name}: {serializer.errors}")
