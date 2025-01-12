# ai_core/components/base.py
from dataclasses import dataclass
from typing import Dict, List, Any


@dataclass
class ComponentConfig:
    name: str
    enabled: bool
    settings: Dict[str, Any]
    dependencies: List[str]


class BaseComponent:
    def __init__(self, config: ComponentConfig):
        self.config = config
        self.initialized = False

    def initialize(self) -> None:
        if not self.initialized:
            self._setup()
            self.initialized = True

    def _setup(self) -> None:
        """
        Setup method to be implemented by child classes.
        Raises:
            NotImplementedError: If child class doesn't implement this method.
        """
        raise NotImplementedError("_setup method must be implemented by child class")