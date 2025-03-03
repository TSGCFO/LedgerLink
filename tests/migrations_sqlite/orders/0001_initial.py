from django.db import migrations, models
import django.utils.timezone
import json


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('customers', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('transaction_id', models.CharField(max_length=100, unique=True)),
                ('close_date', models.DateField()),
                ('reference_number', models.CharField(blank=True, max_length=100, null=True)),
                ('ship_to_name', models.CharField(blank=True, max_length=100, null=True)),
                ('ship_to_company', models.CharField(blank=True, max_length=100, null=True)),
                ('ship_to_address', models.CharField(blank=True, max_length=200, null=True)),
                ('ship_to_address2', models.CharField(blank=True, max_length=200, null=True)),
                ('ship_to_city', models.CharField(blank=True, max_length=100, null=True)),
                ('ship_to_state', models.CharField(blank=True, max_length=50, null=True)),
                ('ship_to_zip', models.CharField(blank=True, max_length=20, null=True)),
                ('ship_to_country', models.CharField(blank=True, max_length=100, null=True)),
                ('weight_lb', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('packages', models.IntegerField(blank=True, null=True)),
                ('volume_cuft', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('line_items', models.IntegerField(blank=True, null=True)),
                ('total_item_qty', models.IntegerField(blank=True, null=True)),
                ('notes', models.TextField(blank=True, null=True)),
                ('carrier', models.CharField(blank=True, max_length=100, null=True)),
                ('sku_quantity', models.JSONField(blank=True, default=dict, null=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('customer', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='orders', to='customers.customer')),
            ],
        ),
    ]