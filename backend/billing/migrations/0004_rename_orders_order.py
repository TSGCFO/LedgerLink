# Generated by Django 5.0.6 on 2024-06-06 16:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0003_rename_order_orders'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Orders',
            new_name='Order',
        ),
    ]
