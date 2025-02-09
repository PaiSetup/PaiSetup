import enum

from steps.step import Step


class DependencyType(enum.Enum):
    Push = enum.auto()
    Pull = enum.auto()


class Proxy:
    def __init__(self, dependency_dispatcher, dependency_type):
        self._dependency_dispatcher = dependency_dispatcher
        self._dependency_type = dependency_type
        self._methods = []

    def add_method(self, method):
        # Validate method count
        if self._dependency_type == DependencyType.Pull and len(self._methods):
            raise ValueError("'Pull' dependencies can only have one handler")

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
        return self._dependency_dispatcher._dispatch(self._methods, self._dependency_type, *args, **kwargs)


class AppendStepStack:
    def __init__(self, dependency_dispatcher, step):
        self._dependency_dispatcher = dependency_dispatcher
        self._step = step

    def _detect_cycle(self):
        try:
            # If this step is already in our stack, there is a dependency cycle.
            idx = self._dependency_dispatcher._step_stack.index(self._step)
        except ValueError:
            # There is no cycle.
            return

        # If the cycle length is 1, we're just self-calling through dependency dispatcher.
        # That is ok.
        if idx == len(self._dependency_dispatcher._step_stack) - 1:
            return

        cycle = self._dependency_dispatcher._step_stack[idx:] + [self._step]
        cycle = "->".join([x.name for x in cycle])
        raise ValueError(f"Dependency cycle detected: {cycle}")

    def __enter__(self, *args, **kwargs):
        self._detect_cycle()
        self._dependency_dispatcher._step_stack.append(self._step)
        return self

    def __exit__(self, *args, **kwargs):
        self._dependency_dispatcher._step_stack.pop()

class DependencyDispatcher:
    """
    This class provides a decoupled way for steps to express dependencies and satisfy them.

    Each step can register one or more of its methods as a dependency handler.
    For example PackageStep can register its 'add_packages' method.
    To achieve this, 'add_packages' method has to be decorated with @dependency_listener.

    Each step can express its dependencies, by calling the handler method on an object od DependencyDispatcher.
    DependencyDispatcher will forward the call to the appriopriate registered handler.
    For example GitStep can express its dependency on 'git' package being installed by calling "dispatcher.add_packages('git')".
    To achieve this the step has to implement push_dependencies().
    """

    def __init__(self, auto_resolve):
        self._accepted_dependency_type = None
        self._proxies = {
            DependencyType.Push: {},
            DependencyType.Pull: {},
        }
        self._auto_resolve = auto_resolve
        self._step_stack = []

    def is_auto_resolve_enabled(self):
        return self._auto_resolve

    def register_handlers(self, step):
        """
        This method detects methods decorated with @dependency_listener and registers them as dependency handlers.
        """
        for method in dir(step.__class__):
            method = getattr(step, method)
            if hasattr(method, "_is_push_dependency_handler"):
                proxy = self._get_proxy(method.__name__, DependencyType.Push, True)
                proxy.add_method(method)
            elif hasattr(method, "_is_pull_dependency_handler"):
                proxy = self._get_proxy(method.__name__, DependencyType.Pull, True)
                proxy.add_method(method)

    def resolve_dependencies(self, steps):
        # Save into variable, because steps may be enabled during iteration.
        enabled_steps = [step for step in steps if step.is_enabled()]

        # Process push dependencies.
        self._accepted_dependency_type = DependencyType.Push
        for step in enabled_steps:
            with AppendStepStack(self, step):
                step.transition_state(Step.State.PushedDeps, self)

        # Process pull dependencies
        self._accepted_dependency_type = DependencyType.Pull
        for step in enabled_steps:
            with AppendStepStack(self, step):
                step.transition_state(Step.State.PulledDeps, self)

        # Disable dependency processing
        self._accepted_dependency_type = None

    def _get_proxy(self, method_name, dependency_type, create_if_missing):
        proxies_group = self._proxies[dependency_type]

        if method_name in proxies_group:
            proxy = proxies_group[method_name]
        elif create_if_missing:
            proxy = Proxy(self, dependency_type)
            proxies_group[method_name] = proxy
        else:
            proxy = None
        return proxy

    def __getattr__(self, method_name):
        if self._accepted_dependency_type is None:
            raise ValueError(f"Dependency dispatcher is currently disabled.")

        proxy = self._get_proxy(method_name, self._accepted_dependency_type, False)
        if proxy is None:
            raise ValueError(f'A dependency on method "{method_name}" was not satisfied')
        else:
            return proxy

    def _dispatch(self, methods, dependency_type, *args, **kwargs):
        for step, method in methods:
            # Acquire current step
            current_step = self._step_stack[-1]

            with AppendStepStack(self, step):
                # Our dependencies must be enabled steps. Implicitly enable them.
                if not step.is_enabled():
                    step._logger.log(f"INFO: Implicitly enabling {step.name} step - used as dependency by {current_step.name} step.")
                    step.set_enabled(True)

                # Our dependencies must execute earlier than us.
                if dependency_type == DependencyType.Pull:
                    step.transition_state(Step.State.PulledDeps, self)
                else:
                    step.transition_state(Step.State.PushedDeps, self)

                # Call our dependency.
                result = method(*args, **kwargs)

                # Validate return value,
                if dependency_type == DependencyType.Pull and result is None:
                    step._logger.push_warning(f"Pull dependency handler {method.__qualname__} returned None. This is unexpected.")
                if dependency_type == DependencyType.Push and result is not None:
                    step._logger.push_warning(f"Push dependency handler {method.__qualname__} returned results. This is unexpected.")

                # Pulled dependencies have only one handler and it returns data
                if dependency_type == DependencyType.Pull:
                    return result




def dependency_listener(func):
    """
    A decorator used for marking methods of Step implementors as dependency listeners. This allows
    other steps to depend on the marked method and call it during push_dependencies phase.
    """
    func._is_push_dependency_handler = True
    return func

def pull_dependency_handler(func):
    func._is_pull_dependency_handler = True
    return func
