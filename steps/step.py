class Step:
    """
    Base class for all steps of setting up the working environment. A step is a logical part
    of the whole process, which can be filtered out by its name. Concrete steps should
    derive from this class and implement one or more of its methods.
    """

    def __init__(self, name):
        self.name = name
        self._enabled = True

    @classmethod
    def setup_external_services(cls, file_writer, env):
        """
        A service is an object shared between all steps which provides some utility functions
        while storing its state internally.
        """
        cls._file_writer = file_writer
        cls._env = env

    def register_as_dependency_listener(self, dependency_dispatcher):
        """
        This method detects methods decorated with @dependency_listener and registers them to the
        dependency dispatcher. Such method can be called by other steps during express_dependencies
        phase. This method must not be implemented by deriving classes.
        """
        methods = dir(self.__class__)
        methods = [getattr(self, x) for x in methods]
        methods = [x for x in methods if hasattr(x, "_is_dependency_listener")]
        for method in methods:
            dependency_dispatcher.register_listener(method)

    def register_env_variables(self):
        """
        This method can be implemented by deriving classes.

        Its goal is to set environment variables in current process. Some steps may add export
        instructions to scripts like .profile, but this is not enough if other steps depend on
        the env vars being set. They will only be set after relogging to the system. Hence
        we also have to set it in the current process.

        It cannot be done in perform(), because the order of execution is undefined. This method
        will always be called before perform() invocations of all other steps.
        """
        pass

    def express_dependencies(self, dependency_dispatcher):
        """
        This method can be implemented by deriving classes.

        It allows to call methods of other steps through the DependencyDispatcher mechanism.
        """
        pass

    def perform(self):
        """
        This method can be implemented by deriving classes.

        It is a main method performing actual operations done by the step. Example operations could
        be creating a file, setting up permissions, downloading a project. Not all steps have to
        implement this. Some of them may exist only to place dependencies on other steps.
        """
        pass

    def is_enabled(self):
        return self._enabled

    def set_enabled(self, value):
        value = bool(value)
        if self._enabled == value:
            raise ValueError("Redundant setter call")
        self._enabled = value

    def is_method_overriden(self, method):
        method_name = method.__name__
        self_dict = self.__class__.__dict__
        class_dict = Step.__dict__
        return method_name in self_dict and self_dict[method_name] != class_dict[method_name]


def dependency_listener(func):
    """
    A decorator used for marking methods of Step implementors as dependency listeners. This allows
    other steps to depend on the marked method and call it during express_dependencies phase.
    """
    func._is_dependency_listener = True
    return func
