# ai_core/examples/code_generation_examples.py
from ..code_generation import CodeGenerator
from django.conf import settings


def model_generation_example():
    """
    Example of generating a Django model
    """
    generator = CodeGenerator(settings.AI_SYSTEM_CONFIG['components']['code_generator'])

    # Model specification
    model_spec = {
        'name': 'Product',
        'fields': [
            {
                'name': 'name',
                'type': 'CharField',
                'params': {'max_length': 100}
            },
            {
                'name': 'price',
                'type': 'DecimalField',
                'params': {
                    'max_digits': 8,
                    'decimal_places': 2
                }
            },
            {
                'name': 'description',
                'type': 'TextField',
                'params': {'blank': True}
            }
        ],
        'meta': {
            'ordering': ['-created_at'],
            'verbose_name': 'Product',
            'verbose_name_plural': 'Products'
        }
    }

    generated_code = generator.generate_model(model_spec)
    return generated_code


def view_generation_example():
    """
    Example of generating a Django view
    """
    generator = CodeGenerator(settings.AI_SYSTEM_CONFIG['components']['code_generator'])

    # View specification
    view_spec = {
        'name': 'ProductListView',
        'type': 'ListView',
        'model': 'Product',
        'mixins': ['LoginRequiredMixin'],
        'methods': [
            {
                'name': 'get_queryset',
                'params': '',
                'body': 'return Product.objects.filter(active=True)'
            }
        ]
    }

    generated_code = generator.generate_view(view_spec)
    return generated_code