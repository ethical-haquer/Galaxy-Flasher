# flash_tool_plugins/__init__.py
from abc import ABC, abstractmethod
from typing import Optional, List
import pkgutil
import importlib

_registered_plugins = {}


def register_plugin(plugin_class):
    """Register a plugin."""
    if not issubclass(plugin_class, FlashToolPlugin):
        raise ValueError("Only FlashToolPlugin subclasses can be registered")
    _registered_plugins[plugin_class.__name__] = plugin_class


class FlashToolPlugin(ABC):
    """Base class for all plugins."""

    def __init__(self, main):
        """Initialize the plugin with the main program."""
        self.main = main

    @abstractmethod
    def test(self):
        """Just a test."""
        pass

    @abstractmethod
    def initialise_buttons(self):
        """Initialise buttons."""
        pass

    @abstractmethod
    def select_partitions(self):
        """Prompt the user to select partitions to flash."""
        pass

    def __init_subclass__(cls, **kwargs):
        """Register this plugin when it's subclassed."""
        register_plugin(cls)


def load_plugins(main) -> List[FlashToolPlugin]:
    """Load plugins from this package."""
    plugins = []
    for importer, modname, ispkg in pkgutil.iter_modules(__path__):
        try:
            importlib.import_module(f"{__name__}.{modname}")
        except Exception as e:
            print(f"Error loading module {modname}: {e}")

    for plugin_name, plugin_class in _registered_plugins.items():
        if issubclass(plugin_class, FlashToolPlugin):
            try:
                plugins.append(plugin_class(main))
            except Exception as e:
                print(f"Error loading plugin {plugin_name}: {e}")

    return plugins
