# ai_core/system.py
from django.conf import settings
from typing import Dict, Type
import importlib
import logging
from .components import BaseComponent, ComponentConfig

logger = logging.getLogger(__name__)


class AISystem:
    _instance = None
    _initialized = False

    def __init__(self):
        if AISystem._instance is not None:
            raise RuntimeError("AISystem is a singleton. Use AISystem.initialize() instead.")
        self.components = {}

    @classmethod
    def initialize(cls):
        """Initialize the AI system singleton"""
        if not cls._initialized:
            cls._instance = cls()
            cls._instance._setup()
            cls._initialized = True
            logger.info("AI System initialized successfully")

    def _setup(self):
        """Set up the AI system components"""
        self.components = {}
        self._load_components()
        self._initialize_components()

    def _load_components(self):
        """Load all enabled components from configuration"""
        config = settings.AI_SYSTEM_CONFIG['components']
        for component_name, component_config in config.items():
            if component_config['enabled']:
                try:
                    component_class = self._get_component_class(component_name)
                    self.components[component_name] = component_class(
                        ComponentConfig(
                            name=component_name,
                            enabled=True,
                            settings=component_config.get('settings', {}),
                            dependencies=component_config.get('dependencies', [])
                        )
                    )
                    logger.info(f"Loaded component: {component_name}")
                except Exception as e:
                    logger.error(f"Failed to load component {component_name}: {str(e)}")

    def _get_component_class(self, component_name: str) -> Type[BaseComponent]:
        """
        Dynamically import and return the component class.
        """
        try:
            # Convert component name to class name (e.g., project_analyzer -> ProjectAnalyzer)
            class_name = ''.join(word.capitalize() for word in component_name.split('_'))
            module = importlib.import_module(f'.components.{component_name}', package='ai_core')
            return getattr(module, class_name)
        except (ImportError, AttributeError) as e:
            logger.error(f"Failed to import component {component_name}: {str(e)}")
            raise

    def _initialize_components(self):
        """Initialize all loaded components in dependency order"""
        initialized = set()

        def initialize_component(name):
            if name in initialized:
                return

            component = self.components[name]
            for dep in component.config.dependencies:
                if dep not in initialized and dep in self.components:
                    initialize_component(dep)

            component.initialize()
            initialized.add(name)
            logger.info(f"Initialized component: {name}")

        for component_name in self.components:
            initialize_component(component_name)

    @classmethod
    def get_component(cls, name: str) -> BaseComponent:
        """
        Get an initialized component by name.
        """
        if not cls._initialized:
            raise RuntimeError("AI System not initialized")

        component = cls._instance.components.get(name)
        if component is None:
            raise KeyError(f"Component not found: {name}")

        return component

    @classmethod
    def is_initialized(cls) -> bool:
        """Check if the AI system is initialized"""
        return cls._initialized

    def __str__(self):
        return f"AISystem(initialized={self._initialized}, components={list(self.components.keys())})"