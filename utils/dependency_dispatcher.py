from enum import Enum
from utils.log import log
from steps.step import Step


class Listener:
    def __init__(self, dependency_dispatcher):
        self._dependency_dispatcher = dependency_dispatcher
        self._methods = []

    def register(self, method):
        # Acquire the step, which is registering the listener
        try:
            step = method.__self__
        except AttributeError:
            raise ValueError("Listener should be a method")
        if not issubclass(step.__class__, Step):
            raise ValueError("Listener should be a method of Step")

        # Save the method along with its step for easy access
        self._methods.append((step, method))

    def __call__(self, *args, **kwargs):
        for step, method in self._methods:
            # If there is a dependency on disabled step, it must be enabled
            if not step.is_enabled():
                if self._dependency_dispatcher.is_auto_resolve_enabled():
                    log(f"INFO: automatic dependency resolving is enabled. Enabling {step.name} step")
                    step.set_enabled(True)
                    step.express_dependencies(self._dependency_dispatcher)
                else:
                    step._warnings.push(f"automatic dependency resolving is disabled, but {method.__qualname__} is used as a dependency.")

            # Call all methods, but return early if any of them returns a value
            result = method(*args, **kwargs)
            if result is not None:
                return result


class DependencyDispatcher:
    """
    This class provides a decoupled way for steps to express dependencies and satisfy them.

    Each step can register one or more of its methods as a dependency handler.
    For example PackageStep can register its 'add_packages' method.
    To achieve this, 'add_packages' method has to be decorated with @dependency_listener.

    Each step can express its dependencies, by calling the handler method on an object od DependencyDispatcher.
    DependencyDispatcher will forward the call to the appriopriate registered handler.
    For example GitStep can express its dependency on 'git' package being installed by calling "dispatcher.add_packages('git')".
    To achieve this the step has to implement express_dependencies().
    """

    def __init__(self, auto_resolve):
        self._listeners = {}
        self._auto_resolve = auto_resolve

    def register_listener(self, method):
        # Create new listener for this method name if neccessary
        method_name = method.__name__
        if method_name not in self._listeners:
            self._listeners[method_name] = Listener(self)

        # Add the method to listener
        self._listeners[method_name].register(method)

    def __getattr__(self, method_name):
        if method_name not in self._listeners:
            raise ValueError(f'A dependency on method "{method_name}" was not satisfied')
        else:
            return self._listeners[method_name]

    def is_auto_resolve_enabled(self):
        return self._auto_resolve
