# ai_core/components/project_analyzer.py
import inspect
import importlib
from typing import Dict, List, Any, Optional, Type
from pathlib import Path
from django.apps import apps
from django.db import models
from django.db.models import Index
from django.apps.config import AppConfig
from django.template.loaders.app_directories import get_app_template_dirs
from django.conf import settings
from django.urls import URLPattern, URLResolver
from django.views.generic import View
from .base import BaseComponent, ComponentConfig


class ProjectAnalyzer(BaseComponent):
    """
    Analyzes Django project structure and provides insights about models, views, and URLs.
    """

    def __init__(self, config: ComponentConfig):
        """
        Initialize the ProjectAnalyzer.
        Args:
            config: Configuration for the analyzer component
        """
        super().__init__(config)
        self.app_registry: Dict[str, Dict[str, Any]] = {}
        self.model_graph: Dict[str, Dict[str, Any]] = {}
        self.ignore_patterns: List[str] = config.settings.get('ignore_patterns', [])

    def _setup(self) -> None:
        """Initialize component by pre-loading app registry"""
        self._load_app_registry()

    def _load_app_registry(self) -> None:
        """Pre-load application registry for faster analysis"""
        for app_config in apps.get_app_configs():
            if not self._is_system_app(app_config.name):
                self.app_registry[app_config.name] = self._get_app_config(app_config)

    def analyze_project(self, full_analysis: bool = False, components: List[str] = None) -> Dict[str, Any]:
        """
        Analyzes the entire Django project structure or specific components.
        Args:
            full_analysis: Whether to perform a full analysis
            components: List of specific components to analyze ('models', 'views', 'templates', etc.)
        Returns:
            Dictionary containing analysis results
        """
        results = {}

        # Determine which components to analyze
        if components is None:
            components = ['apps', 'models', 'views', 'urls', 'templates']

        # Analyze each requested component
        if 'apps' in components:
            results['apps'] = self.analyze_apps()
        if 'models' in components:
            results['models'] = self.analyze_models()
        if 'views' in components:
            results['views'] = self.analyze_views()
        if 'urls' in components:
            results['urls'] = self.analyze_urls()
        if 'templates' in components:
            results['templates'] = self.analyze_templates()

        # Add statistics
        results['stats'] = self._generate_stats()

        # Add detailed analysis if requested
        if full_analysis:
            results['detailed_analysis'] = self._perform_detailed_analysis()

        return results

    def analyze_apps(self) -> Dict[str, Dict[str, Any]]:
        """
        Analyzes all installed Django apps.
        Returns:
            Dictionary containing app analysis data
        """
        app_data = {}
        for app_config in apps.get_app_configs():
            if not self._is_system_app(app_config.name):
                app_data[app_config.name] = {
                    'path': str(Path(app_config.path)),
                    'models': self._get_app_models(app_config),
                    'config': self._get_app_config(app_config)
                }
        return app_data

    def analyze_models(self) -> Dict[str, Dict[str, Any]]:
        """
        Analyzes all models in the project.
        Returns:
            Dictionary containing model analysis
        """
        models_data = {}
        for model in apps.get_models():
            if not self._is_system_app(model._meta.app_label):
                model_key = f"{model._meta.app_label}.{model.__name__}"
                models_data[model_key] = {
                    'fields': self._get_model_fields(model),
                    'relations': self._get_model_relations(model),
                    'meta': self._get_model_meta(model),
                    'methods': self._get_model_methods(model)
                }

                # Add to model graph for relationship analysis
                self.model_graph[model_key] = models_data[model_key]
        return models_data

    def analyze_views(self) -> Dict[str, Any]:
        """
        Analyzes all views in the project.
        Returns:
            Dictionary containing view analysis
        """
        views_data = {}
        for app_config in apps.get_app_configs():
            if not self._is_system_app(app_config.name):
                try:
                    views_module = importlib.import_module(f"{app_config.name}.views")
                    views_data.update(self._analyze_module_views(views_module, app_config.name))
                except ImportError:
                    continue
        return views_data

    def analyze_urls(self) -> Dict[str, Any]:
        """
        Analyzes URL patterns in the project.
        Returns:
            Dictionary containing URL analysis
        """
        urls_data = {
            'patterns': [],
            'namespaces': {}
        }

        for app_config in apps.get_app_configs():
            if not self._is_system_app(app_config.name):
                try:
                    urls_module = importlib.import_module(f"{app_config.name}.urls")
                    urls_data['patterns'].extend(self._analyze_url_patterns(getattr(urls_module, 'urlpatterns', [])))
                    urls_data['namespaces'][app_config.name] = self._analyze_url_namespace(urls_module)
                except (ImportError, AttributeError):
                    continue

        return urls_data

    def analyze_templates(self) -> Dict[str, Any]:
        """
        Analyzes templates in the project.
        Returns:
            Dictionary containing template analysis
        """
        templates_data = {
            'templates': [],
            'template_dirs': []
        }

        # Get all template directories
        template_dirs = []
        if hasattr(settings, 'TEMPLATES'):
            for template_config in settings.TEMPLATES:
                if 'DIRS' in template_config:
                    template_dirs.extend(template_config['DIRS'])

        # Add app template directories
        template_dirs.extend(get_app_template_dirs('templates'))
        templates_data['template_dirs'] = [str(path) for path in template_dirs]

        # Analyze templates in each directory
        for template_dir in template_dirs:
            templates_data['templates'].extend(
                self._analyze_template_directory(Path(template_dir))
            )

        return templates_data

    def _is_system_app(self, app_name: str) -> bool:
        """
        Checks if the app is a Django system app.
        Args:
            app_name: Name of the application
        Returns:
            bool: True if system app, False otherwise
        """
        return app_name.startswith('django.') or app_name in [
            'django_extensions',
            'rest_framework',
            'channels'
        ]

    def _get_app_models(self, app_config: AppConfig) -> Dict[str, Dict[str, Any]]:
        """
        Gets all models for a specific app.
        Args:
            app_config: Django application configuration
        Returns:
            Dictionary containing model information
        """
        models_data = {}
        for model in app_config.get_models():
            models_data[model.__name__] = {
                'fields': self._get_model_fields(model),
                'relations': self._get_model_relations(model),
                'meta': self._get_model_meta(model),
                'methods': self._get_model_methods(model)
            }
        return models_data

    def _get_model_fields(self, model: Type[models.Model]) -> Dict[str, Dict[str, Any]]:
        """
        Gets field information for a model.
        Args:
            model: Django model class
        Returns:
            Dictionary containing field information
        """
        fields = {}
        for field in model._meta.fields:
            fields[field.name] = {
                'type': field.__class__.__name__,
                'required': not field.null,
                'unique': field.unique,
                'params': self._get_field_params(field)
            }
        return fields

    def _get_field_params(self, field: models.Field) -> Dict[str, Any]:
        """
        Gets parameters for a model field.
        Args:
            field: Django model field
        Returns:
            Dictionary containing field parameters
        """
        params = {}
        for key, value in field.__dict__.items():
            if (not key.startswith('_') and
                    key not in ['null', 'blank', 'unique'] and
                    not callable(value)):
                params[key] = str(value) if not isinstance(value, (bool, int, float, str, list, dict)) else value
        return params

    def _get_model_relations(self, model: Type[models.Model]) -> Dict[str, Dict[str, Any]]:
        """
        Gets relation information for a model.
        Args:
            model: Django model class
        Returns:
            Dictionary containing relation information
        """
        relations = {}
        for field in model._meta.get_fields():
            if field.is_relation:
                relations[field.name] = {
                    'type': field.__class__.__name__,
                    'model': field.related_model.__name__,
                    'reverse_name': field.remote_field.name if hasattr(field, 'remote_field') else None,
                    'on_delete': str(field.remote_field.on_delete) if hasattr(field.remote_field, 'on_delete') else None
                }
        return relations

    def _get_model_meta(self, model: Type[models.Model]) -> Dict[str, Any]:
        """
        Gets meta information for a model.
        Args:
            model: Django model class
        Returns:
            Dictionary containing meta information
        """
        meta = model._meta
        return {
            'db_table': meta.db_table,
            'ordering': meta.ordering or [],
            'indexes': [
                {
                    'fields': index.fields,
                    'unique': getattr(index, 'unique', False) if isinstance(index, Index) else False
                }
                for index in meta.indexes
            ],
            'constraints': [
                str(constraint) for constraint in meta.constraints
            ] if hasattr(meta, 'constraints') else []
        }

    def _get_model_methods(self, model: Type[models.Model]) -> List[str]:
        """
        Gets list of model methods.
        Args:
            model: Django model class
        Returns:
            List of method names
        """
        return [
            method for method in dir(model)
            if callable(getattr(model, method)) and
               not method.startswith('_') and
               method not in ['save', 'delete']
        ]

    def _get_app_config(self, app_config: AppConfig) -> Dict[str, Any]:
        """
        Gets configuration details for an app.
        Args:
            app_config: Django application configuration
        Returns:
            Dictionary containing app configuration
        """
        return {
            'name': app_config.name,
            'verbose_name': app_config.verbose_name,
            'path': str(app_config.path),
            'models_module': str(app_config.models_module) if app_config.models_module else None,
            'default_auto_field': getattr(app_config, 'default_auto_field', None)
        }

    def _analyze_module_views(self, module, app_name: str) -> Dict[str, Any]:
        """
        Analyzes views in a specific module.
        Args:
            module: Python module containing views
            app_name: Name of the Django app
        Returns:
            Dictionary containing view analysis
        """
        views_data = {}
        for item_name in dir(module):
            item = getattr(module, item_name)
            if self._is_view_class(item):
                views_data[f"{app_name}.{item_name}"] = {
                    'type': 'class',
                    'base_classes': [base.__name__ for base in item.__bases__],
                    'methods': self._get_view_methods(item),
                    'attributes': self._get_view_attributes(item)
                }
            elif self._is_view_function(item):
                views_data[f"{app_name}.{item_name}"] = {
                    'type': 'function',
                    'parameters': self._get_function_parameters(item),
                    'decorators': self._get_function_decorators(item)
                }
        return views_data

    def _analyze_url_patterns(self, urlpatterns: List) -> List[Dict[str, Any]]:
        """
        Analyzes URL patterns.
        Args:
            urlpatterns: List of URL patterns
        Returns:
            List of dictionaries containing URL pattern analysis
        """
        patterns = []
        for pattern in urlpatterns:
            if isinstance(pattern, URLPattern):
                patterns.append({
                    'path': str(pattern.pattern),
                    'view': self._get_view_name(pattern.callback),
                    'name': getattr(pattern, 'name', None),
                    'parameters': self._extract_url_parameters(str(pattern.pattern))
                })
            elif isinstance(pattern, URLResolver):
                patterns.extend(self._analyze_url_patterns(pattern.url_patterns))
        return patterns

    def _analyze_url_namespace(self, urls_module) -> Dict[str, Any]:
        """
        Analyzes URL namespace configuration.
        Args:
            urls_module: URLs module
        Returns:
            Dictionary containing namespace information
        """
        return {
            'app_name': getattr(urls_module, 'app_name', None),
            'namespace': getattr(urls_module, 'namespace', None)
        }

    def _analyze_template_directory(self, directory: Path) -> List[Dict[str, Any]]:
        """
        Analyzes templates in a directory.
        Args:
            directory: Path object pointing to template directory
        Returns:
            List of dictionaries containing template analysis
        """
        templates = []
        if directory.exists():
            for template_file in directory.rglob('*.html'):
                try:
                    with template_file.open('r', encoding='utf-8') as f:
                        content = f.read()
                        templates.append({
                            'path': str(template_file.relative_to(directory)),
                            'extends': self._find_template_extends(content),
                            'blocks': self._find_template_blocks(content),
                            'includes': self._find_template_includes(content),
                            'static_files': self._find_static_files(content)
                        })
                except (IOError, UnicodeDecodeError):
                    continue
        return templates

    def _is_view_class(self, obj) -> bool:
        """
        Checks if an object is a view class.
        """
        return isinstance(obj, type) and issubclass(obj, View)

    def _is_view_function(self, obj) -> bool:
        """
        Checks if an object is a view function.
        """
        return callable(obj) and hasattr(obj, '__module__')

    def _get_view_methods(self, view_class) -> Dict[str, Any]:
        """
        Gets methods from a view class.
        """
        return {
            name: {
                'parameters': self._get_function_parameters(method),
                'decorators': self._get_function_decorators(method)
            }
            for name, method in inspect.getmembers(view_class, predicate=inspect.isfunction)
            if not name.startswith('_')
        }

    def _get_view_attributes(self, view_class) -> Dict[str, Any]:
        """
        Gets attributes from a view class.
        """
        return {
            name: str(value)
            for name, value in inspect.getmembers(view_class)
            if not name.startswith('_') and not callable(value)
        }

    def _get_function_parameters(self, func) -> List[str]:
        """
        Gets function parameter names.
        """
        return list(inspect.signature(func).parameters.keys())

    def _get_function_decorators(self, func) -> List[str]:
        """
        Gets function decorator names.
        """
        return [
            d.__name__ for d in getattr(func, '__decorators__', [])
        ] if hasattr(func, '__decorators__') else []

    def _get_view_name(self, view_func) -> str:
        """
        Gets the name of a view function or class.
        """
        if hasattr(view_func, '__name__'):
            return view_func.__name__
        return view_func.__class__.__name__

    def _extract_url_parameters(self, pattern: str) -> List[str]:
        """
        Extracts parameter names from URL pattern.
        """
        import re
        return re.findall(r'<([^>]+)>', pattern)

    def _find_template_extends(self, content: str) -> Optional[str]:
        """
        Finds template inheritance.
        """
        import re
        match = re.search(r'{%\s*extends\s+["\']([^"\']+)["\']\s*%}', content)
        return match.group(1) if match else None

    def _find_template_blocks(self, content: str) -> List[str]:
        """
        Finds template blocks.
        """
        import re
        return re.findall(r'{%\s*block\s+([^\s%]+)\s*%}', content)

    def _find_template_includes(self, content: str) -> List[str]:
        """
        Finds template includes.
        """
        import re
        return re.findall(r'{%\s*include\s+["\']([^"\']+)["\']\s*%}', content)

    def _find_static_files(self, content: str) -> List[str]:
        """
        Finds static file references.
        """
        import re
        return re.findall(r'{%\s*static\s+["\']([^"\']+)["\']\s*%}', content)

    def _generate_stats(self) -> Dict[str, int]:
        """
        Generates analysis statistics.
        Returns:
            Dictionary containing analysis statistics
        """
        return {
            'apps_analyzed': len(self.app_registry),
            'models_found': len(self.model_graph),
            'fields_analyzed': sum(
                len(model_data.get('fields', {}))
                for models in self.model_graph.values()
                for model_data in models.values()
            ),
            'relations_found': sum(
                len(model_data.get('relations', {}))
                for models in self.model_graph.values()
                for model_data in models.values()
            )
        }

    def _perform_detailed_analysis(self) -> Dict[str, Any]:
        """
        Performs a detailed analysis of the project.
        Returns:
            Dictionary containing detailed analysis results
        """
        return {
            'model_relationships': self._analyze_model_relationships(),
            'model_complexity': self._analyze_model_complexity(),
            'code_patterns': self._analyze_code_patterns()
        }

    def _analyze_model_relationships(self) -> Dict[str, List[Dict[str, str]]]:
        """
        Analyzes relationships between models.
        Returns:
            Dictionary containing model relationship information
        """
        relationships = {}
        for app_config in apps.get_app_configs():
            if not self._is_system_app(app_config.name):
                for model in app_config.get_models():
                    model_relations = []
                    for field in model._meta.get_fields():
                        if field.is_relation:
                            model_relations.append({
                                'from': model.__name__,
                                'to': field.related_model.__name__,
                                'type': field.__class__.__name__
                            })
                    if model_relations:
                        relationships[model.__name__] = model_relations
        return relationships

    def _analyze_model_complexity(self) -> Dict[str, Dict[str, int]]:
        """
        Analyzes complexity of models.
        Returns:
            Dictionary containing model complexity metrics
        """
        complexity = {}
        for app_config in apps.get_app_configs():
            if not self._is_system_app(app_config.name):
                for model in app_config.get_models():
                    complexity[model.__name__] = {
                        'fields_count': len(model._meta.fields),
                        'relations_count': len([f for f in model._meta.get_fields() if f.is_relation]),
                        'indexes_count': len(model._meta.indexes),
                        'constraints_count': len(getattr(model._meta, 'constraints', []))
                    }
        return complexity

    def _analyze_code_patterns(self) -> Dict[str, List[str]]:
        """
        Analyzes common code patterns in the project.
        Returns:
            Dictionary containing identified code patterns
        """
        return {
            'model_patterns': [],  # To be implemented
            'field_patterns': []  # To be implemented
        }