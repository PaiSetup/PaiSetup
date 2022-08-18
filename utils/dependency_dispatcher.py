from enum import Enum
from utils.log import log


class Listener:
    def __init__(self, dependency_dispatcher):
        self._dependency_dispatcher = dependency_dispatcher
        self._methods = []

    def register(self, method):
        self._methods.append(method)

    def __call__(self, *args, **kwargs):
        kwargs['dependency_dispatcher'] = self._dependency_dispatcher
        for method in self._methods:
            method(*args, **kwargs)


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
        self._dummy_listener = Listener(self)
        self._missing_listeners = set()

    def register_listener(self, method):
        method_name = method.__name__
        if method_name not in self._listeners:
            self._listeners[method_name] = Listener(self)
        self._listeners[method_name].register(method)

    def __getattr__(self, method_name):
        if method_name not in self._listeners:
            self._missing_listeners.add(method_name)
            return self._dummy_listener
        else:
            return self._listeners[method_name]

    def summary(self):
        for missing_listener in self._missing_listeners:
            log(f'WARNING: dependencies on method "{missing_listener}" was not satisfied')
