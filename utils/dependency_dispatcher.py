from enum import Enum
from utils.log import log


class DependencyListenerConflict(Exception):
    def __init__(self, method_name):
        self.method_name = method_name

    def __str__(self):
        return f"Multiple listeners registered for method '{self.method_name}'"


class DependencyDispatcher:
    """
    This class provides a decoupled way for steps to express dependencies and satisfy them.

    Each step can register one or more of its methods as a dependency handler.
    For example PackageStep can register its 'add_packages' method.
    To achieve this the step has to implement register_as_dependency_listener().

    Each step can also express its dependencies, by calling the handler method on an object od DependencyDispatcher.
    DependencyDispatcher will forward the call to the appriopriate registered handler.
    For example GitStep can express its dependency on 'git' package being installed by calling "dispatcher.add_packages('git')".
    To achieve this the step has to implement express_dependencies().
    """

    def __init__(self):
        self._listeners = {}
        self._missing_listeners = set()

    def register_listener(self, method):
        method_name = method.__name__
        if method_name in self._listeners:
            raise DependencyListenerConflict(method_name)
        self._listeners[method_name] = method

    def __getattr__(self, method_name):
        if method_name not in self._listeners:
            self._missing_listeners.add(method_name)
            return self._dummy_method
        else:
            return self._listeners[method_name]

    def _dummy_method(*args, **kwargs):
        pass

    def summary(self):
        for missing_listener in self._missing_listeners:
            log(f'WARNING: dependencies on method "{missing_listener}" was not satisfied')
