# Generated by Django 5.0.7 on 2024-08-14 03:29

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('customer_services', '0001_initial'),
        ('customers', '0003_alter_customer_id'),
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('invoice_date', models.DateTimeField(auto_now_add=True)),
                ('due_date', models.DateTimeField(blank=True, null=True)),
                ('total_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('currency', models.CharField(choices=[('USD', 'US Dollar'), ('CAD', 'Canadian Dollar')], max_length=3)),
                ('status', models.CharField(default='Generated', max_length=20)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='customers.customer')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='orders.order')),
            ],
        ),
        migrations.CreateModel(
            name='Charge',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('transaction_id', models.IntegerField()),
                ('close_date', models.DateTimeField(blank=True, null=True)),
                ('reference_number', models.CharField(max_length=100)),
                ('ship_to_name', models.CharField(blank=True, max_length=100, null=True)),
                ('ship_to_company', models.CharField(blank=True, max_length=100, null=True)),
                ('ship_to_address', models.CharField(blank=True, max_length=200, null=True)),
                ('ship_to_address2', models.CharField(blank=True, max_length=200, null=True)),
                ('ship_to_city', models.CharField(blank=True, max_length=100, null=True)),
                ('ship_to_state', models.CharField(blank=True, max_length=50, null=True)),
                ('ship_to_zip', models.CharField(blank=True, max_length=20, null=True)),
                ('ship_to_country', models.CharField(blank=True, max_length=50, null=True)),
                ('weight_lb', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('line_items', models.IntegerField(blank=True, null=True)),
                ('sku_quantity', models.JSONField(blank=True, null=True)),
                ('total_item_qty', models.IntegerField(blank=True, null=True)),
                ('volume_cuft', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('packages', models.IntegerField(blank=True, null=True)),
                ('notes', models.TextField(blank=True, null=True)),
                ('carrier', models.CharField(blank=True, max_length=50, null=True)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('currency', models.CharField(choices=[('USD', 'US Dollar'), ('CAD', 'Canadian Dollar')], max_length=3)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='customers.customer')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='charges', to='orders.order')),
                ('service', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='customer_services.customerservice')),
                ('invoice', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='charges', to='billing.invoice')),
            ],
        ),
    ]