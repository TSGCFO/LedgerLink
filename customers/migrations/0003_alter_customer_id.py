# Generated by Django 5.0.7 on 2024-07-29 00:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customers', '0002_rename_customers_customer'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]
