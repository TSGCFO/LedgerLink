# ai_core/components/context_manager.py
from django.db import models
from django.core.cache import cache
from . import BaseComponent, ComponentConfig
from ..models import ProjectContext
from typing import Dict


class ContextManager(BaseComponent):
    def __init__(self, config: ComponentConfig):
        super().__init__(config)
        self.cache_timeout = config.settings.get('cache_timeout', 3600)

    def _setup(self):
        """Initialize the context manager"""
        pass

    def get_context(self, key: str) -> Dict:
        """
        Retrieves context data with caching.
        """
        cache_key = f'context_{key}'
        context = cache.get(cache_key)

        if context is None:
            try:
                context = ProjectContext.objects.get(key=key).value
                cache.set(cache_key, context, self.cache_timeout)
            except ProjectContext.DoesNotExist:
                context = {}

        return context

    def set_context(self, key: str, value: Dict):
        """
        Updates context data with caching.
        """
        ProjectContext.objects.update_or_create(
            key=key,
            defaults={'value': value}
        )
        cache.set(f'context_{key}', value, self.cache_timeout)

    def delete_context(self, key: str):
        """
        Deletes context data and removes it from cache.
        """
        ProjectContext.objects.filter(key=key).delete()
        cache.delete(f'context_{key}')

    def clear_context(self):
        """
        Clears all context data.
        """
        ProjectContext.objects.all().delete()
        cache.clear()

    def get_all_contexts(self) -> Dict:
        """
        Retrieves all context data.
        """
        contexts = {}
        for context in ProjectContext.objects.all():
            contexts[context.key] = context.value
        return contexts