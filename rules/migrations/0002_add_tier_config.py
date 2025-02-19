from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('rules', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='advancedrule',
            name='tier_config',
            field=models.JSONField(
                blank=True,
                default=dict,
                help_text="Configuration for tiered calculations: {'ranges': [{'min': x, 'max': y, 'multiplier': z}], 'excluded_skus': []}"
            ),
        ),
    ] 