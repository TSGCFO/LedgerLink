from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='priority',
            field=models.CharField(blank=True, choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('urgent', 'Urgent')], max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='status',
            field=models.CharField(blank=True, choices=[('new', 'New'), ('processing', 'Processing'), ('shipped', 'Shipped'), ('delivered', 'Delivered'), ('cancelled', 'Cancelled')], max_length=20, null=True),
        ),
    ]