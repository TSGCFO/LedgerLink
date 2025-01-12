# ai_core/apps.py
from django.apps import AppConfig
from django.conf import settings


class AICoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ai_core'

    def ready(self):
        from .system import AISystem
        from . import signals



        if hasattr(settings, 'AI_SYSTEM_CONFIG') and settings.AI_SYSTEM_CONFIG['enabled']:
            AISystem.initialize()