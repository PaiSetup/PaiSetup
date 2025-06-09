import enum

from steps.step import Step


class DependencyResolutionMode(enum.Enum):
    none = "none"
    pull = "pull"
    pull_and_push = "pull_and_push"


class DependencyType(enum.Enum):
    """
    There are two types of dependencies.
    Push dependencies transfer data from source step (in push_dependencies) to the
    destination step (the one with @push_dependency_handler)
    Pull dependencies retrieve data from destination step (the one with @pull_dependency_handler)
    and make them available for the source step (in pull_dependencies).
    All pull deps execute after all push deps.
    """

    Push = enum.auto()
    Pull = enum.auto()


class Proxy:
    """
    This class stores all methods serving as a handle for a given dependency name.

    Example: consider a dependency called "set_default_home_page". Multiple steps can implement
    it, like FirefoxStep, EdgeStep and ChromeStep. Each of them would have its own method annotated
        @push_dependency_handler
        def set_default_home_page(self, page):
            ...
    Whenever a different step called dependency_dispatcher.set_default_home_page(), this call would
    be propagated to a single Proxy object containing 3 different methods. In case of push dependencies
    all 3 methods will be called. Pull dependencies can have only 1 method per Proxy.
    """

    def __init__(self, dependency_dispatcher, dependency_type):
        self._dependency_dispatcher = dependency_dispatcher
        self._dependency_type = dependency_type
        self._methods = []

    def get_methods(self):
        return self._methods

    def add_method(self, method):
        # Validate method count
        if self._dependency_type == DependencyType.Pull and len(self._methods):
            raise ValueError("'Pull' dependencies can only have one handler")

        # Acquire the step, which is registering the handler
        try:
            step = method.__self__
        except AttributeError:
            raise ValueError("Handler should be a method")
        if not issubclass(step.__class__, Step):
            raise ValueError("Handler should be a method of Step")

        # Save the method along with its step for easy access
        self._methods.append(method)

    def __call__(self, *args, **kwargs):
        return self._dependency_dispatcher._dispatch(self._methods, self._dependency_type, *args, **kwargs)


class SuperNiceObject:
    def __init__(self):
        self._get_items_left = 50

    def __getattr__(self, _):
        return self

    def __len__(self, _):
        return 0

    def __getitem__(self, _):
        if self._get_items_left == 0:
            raise TimeoutError("Do not place loops inside pull_dependencies()")
        else:
            self._get_items_left -= 1
            return SuperNiceObject()

    def __truediv__(self, _):
        return self

    def __call__(self, _):
        return self


class FakeDependencyDispatcher:
    def __init__(self):
        self.is_fake = True
        self.calls = set()

    def __getattr__(self, method_name):
        if not method_name.startswith("_"):
            self.calls.add(method_name)

        def func(*args, **kwargs):
            return SuperNiceObject()

        return func


class DependencyGraph:
    def __init__(self, allow_unsatisfied_push_dependencies):
        self._allow_unsatisfied_push_dependencies = allow_unsatisfied_push_dependencies
        self._step_to_methods_push_deps = {}
        self._step_to_methods_pull_deps = {}
        self._steps_to_enable = []

    def get_steps_to_enable(self):
        return self._steps_to_enable

    def inspect_steps(self, steps, proxies, resolution_mode):
        enabled_steps = [step for step in steps if step.is_enabled()]

        use_push = resolution_mode == DependencyResolutionMode.pull_and_push
        use_pull = resolution_mode in [DependencyResolutionMode.pull_and_push, DependencyResolutionMode.pull]

        for step in enabled_steps:
            if use_push:
                dispatcher = FakeDependencyDispatcher()
                step.push_dependencies(dispatcher)
                self._step_to_methods_push_deps[step] = self._retrieve_dependent_methods(
                    dispatcher.calls, proxies[DependencyType.Push], True, step, enabled_steps
                )
            if use_pull:
                dispatcher = FakeDependencyDispatcher()
                step.pull_dependencies(dispatcher)
                self._step_to_methods_pull_deps[step] = self._retrieve_dependent_methods(
                    dispatcher.calls, proxies[DependencyType.Pull], False, step, enabled_steps
                )

    def _retrieve_dependent_methods(self, calls, proxies, is_push, step, enabled_steps):
        # Retrieve methods we depend on.
        dependent_methods = set()
        for method_name in calls:
            if method_name not in proxies:
                if is_push and self._allow_unsatisfied_push_dependencies:
                    # TODO pass logger here...
                    print(f"WARNING: ignoring dependency {method_name}, because no matching handler was found.")
                    continue
                else:
                    raise ValueError(f'A dependency on method "{method_name}" was not satisfied')

            methods = proxies[method_name].get_methods()
            for method in methods:
                dependent_methods.add(method)

        # Make sure all dependent steps are already enabled. If not, they will be implicitly enabled
        # and added to this loop.
        for dependent_method in dependent_methods:
            dependent_step = dependent_method.__self__
            if dependent_step not in enabled_steps:
                enabled_steps.append(dependent_step)
                self._steps_to_enable.append((dependent_step, step))

        # Store dependent methods for this step.
        return dependent_methods


class DependencyDispatcher:
    """
    This class provides a decoupled way for steps to express dependencies and satisfy them.

    Each step can register one or more of its methods as a dependency handler.
    For example PackageStep can register its 'add_packages' method.
    To achieve this, 'add_packages' method has to be decorated with @push_dependency_handler.

    Each step can express its dependencies, by calling the handler method on an object od DependencyDispatcher.
    DependencyDispatcher will forward the call to the appriopriate registered handler.
    For example GitStep can express its dependency on 'git' package being installed by calling "dispatcher.add_packages('git')".
    To achieve this the step has to implement push_dependencies().
    """

    def __init__(self, resolution_mode, allow_unsatisfied_push_dependencies):
        self.is_fake = False
        self._resolution_mode = resolution_mode
        self._allow_unsatisfied_push_dependencies = allow_unsatisfied_push_dependencies
        self._current_dependency_type = None
        self._proxies = {
            DependencyType.Push: {},
            DependencyType.Pull: {},
        }

    def register_handlers(self, step):
        """
        This method detects methods decorated with @push_dependency_handler and registers them as dependency handlers.
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
        # Inspect dependencies between steps and build a graph.
        graph = DependencyGraph(self._allow_unsatisfied_push_dependencies)
        graph.inspect_steps(steps, self._proxies, self._resolution_mode)

        # Implicitly enable steps that were disabled, but were required by the graph.
        for step, consumer_step in graph.get_steps_to_enable():
            step._logger.log(f"INFO: Implicitly enabling {step.name} step - used as dependency by {consumer_step.name} step.")
            step.set_enabled(True)
        enabled_steps = [step for step in steps if step.is_enabled()]

        # Process push dependencies.
        self._current_dependency_type = DependencyType.Push
        for step in enabled_steps:
            step.push_dependencies(self)

        # Process pull dependencies.
        self._current_dependency_type = DependencyType.Pull
        for step in enabled_steps:
            step.pull_dependencies(self)

        # Disable dependency processing
        self._current_dependency_type = None

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
        if self._current_dependency_type is None:
            raise ValueError("Dependency processing is disabled.")

        proxy = self._get_proxy(method_name, self._current_dependency_type, False)
        if proxy is None:
            if self._allow_unsatisfied_push_dependencies and self._current_dependency_type is DependencyType.Push:
                return lambda *args, **kwargs: None
            else:
                raise ValueError(f'A dependency on method "{method_name}" was not satisfied')
        else:
            return proxy

    def _dispatch(self, methods, dependency_type, *args, **kwargs):
        for method in methods:
            # Call our dependency.
            result = method(*args, **kwargs)

            # Validate return value
            step = method.__self__
            if dependency_type == DependencyType.Pull and result is None:
                step._logger.push_warning(f"Pull dependency handler {method.__qualname__} returned None. This is unexpected.")
            if dependency_type == DependencyType.Push and result is not None:
                step._logger.push_warning(f"Push dependency handler {method.__qualname__} returned results. This is unexpected.")

            # Pulled dependencies have only one handler and it returns data
            if dependency_type == DependencyType.Pull:
                return result

    def enable_external_dependency_pulling(self):
        class Context:
            def __init__(self, dependency_dispatcher):
                self._dependency_dispatcher = dependency_dispatcher

            def __enter__(self, *args, **kwargs):
                self._saved_type = self._dependency_dispatcher._current_dependency_type
                self._dependency_dispatcher._current_dependency_type = DependencyType.Pull
                return self

            def __exit__(self, *args, **kwargs):
                self._dependency_dispatcher._current_dependency_type = self._saved_type

        return Context(self)


def push_dependency_handler(func):
    """
    A decorator used for marking methods of Step implementors as dependency handlers. This allows
    other steps to depend on the marked method and call it during push_dependencies phase.
    """
    func._is_push_dependency_handler = True
    return func


def pull_dependency_handler(func):
    """
    A decorator used for marking methods of Step implementors as dependency handlers. This allows
    other steps to depend on the marked method and call it during pull_dependencies phase.
    """
    func._is_pull_dependency_handler = True
    return func
