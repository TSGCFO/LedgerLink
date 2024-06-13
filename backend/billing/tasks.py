# billing/tasks.py

from azure.storage.blob import BlobServiceClient
import pandas as pd
from celery import shared_task
from django.conf import settings
from .models import Order, Customer
from .serializers import OrderSerializer  # Ensure this matches the actual name of your serializer

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
        blob_data = blob_client.download_blob().readall()

        # Read the Excel file into a pandas DataFrame
        df = pd.read_excel(blob_data)

        # Ensure columns are properly mapped to the Order model fields
        df.rename(columns={
            'Customer ID': 'customer',
            'Reference Number': 'reference_number',
            'Ship To Name': 'ship_to_name',
            'Ship To Company': 'ship_to_company',
            'Ship To Address': 'ship_to_address',
            'Ship To Address2': 'ship_to_address2',
            'Ship To City': 'ship_to_city',
            'Ship To State': 'ship_to_state',
            'Ship To Zip': 'ship_to_zip',
            'Ship To Country': 'ship_to_country',
            'Carrier': 'carrier',
            'Total Weight (lb)': 'total_weight_lb',
            'Line Items': 'line_items',
            'SKU Quantity': 'sku_quantity',
            'Total Item Quantity': 'total_item_qty',
            'Volume (cuft)': 'volume_cuft',
            'Packages': 'packages',
            'Mark For Lists': 'markfor_lists',
            'Ship Service': 'ship_service',
            'Warehouse Instructions': 'warehouse_instructions',
            'Allocation Status': 'allocation_status',
            'ASN Sent Date': 'asn_sent_date',
            'Batch ID': 'batch_id',
            'Batch Name': 'batch_name',
            'Bill of Lading': 'bill_of_lading',
            'Billing Type': 'billing_type',
            'Cancel Date': 'cancel_date',
            'Confirm ASN Sent Date': 'confirm_asn_sent_date',
            'Earliest Ship Date': 'earliest_ship_date',
            'End of Day Request Date': 'end_of_day_request_date',
            'Load Number': 'load_number',
            'Load Out Percent': 'load_out_percent',
            'Load Out Date': 'load_out_date',
            'Mark For Name ID': 'markfor_name_id',
            'Master Bill of Lading': 'master_bill_of_lading',
            'Pack Done Date': 'pack_done_date',
            'Parcel Label Type': 'parcel_label_type',
            'Pick Done Date': 'pick_done_date',
            'Pick Job Assignee': 'pick_job_assignee',
            'Pick Job ID': 'pick_job_id',
            'Pick Ticket Print Date': 'pick_ticket_print_date',
            'Pickup Date': 'pickup_date',
            'Purchase Order': 'purchase_order',
            'Retailer ID': 'retailer_id',
            'Ship To Email': 'ship_to_email',
            'Ship To Phone': 'ship_to_phone',
            'Small Parcel Ship Date': 'small_parcel_ship_date',
            'Status': 'status',
            'Time Zone': 'time_zone',
            'Tracking Number': 'tracking_number',
            'Volume (m3)': 'volume_m3',
            'Warehouse': 'warehouse',
            'Total Weight (kg)': 'total_weight_kg',
            'Created By': 'created_by',
            'Updated By': 'updated_by',
            'Create Source': 'create_source',
        }, inplace=True)

        # Convert the DataFrame to a list of dictionaries
        order_data = df.to_dict(orient='records')

        for order in order_data:
            customer_id = order.pop('customer')
            try:
                customer = Customer.objects.get(pk=customer_id)
            except Customer.DoesNotExist:
                print(f"Customer ID {customer_id} does not exist, skipping order.")
                continue
            order['customer'] = customer.pk  # Use the customer primary key

            # Serialize and save the orders
            serializer = OrderSerializer(data=order)
            if serializer.is_valid():
                serializer.save()
                print(f"Successfully imported order with reference number {order['reference_number']} from {blob.name}")
            else:
                print(f"Error importing order from {blob.name}: {serializer.errors}")

        # Optionally delete the blob after processing
        blob_client.delete_blob()
