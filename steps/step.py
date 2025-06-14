import enum

from utils.services.env import EnvManager
from utils.services.file_writer import FileWriter
from utils.services.logger import Logger
from utils.services.perf_analyzer import PerfAnalyzer


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
    def setup_external_services(cls, root_dir, logs_dir, enable_perf_analyzer, enable_logger):
        """
        A service is an object shared between all steps which provides some utility functions
        while storing its state internally.
        """
        if hasattr(cls, "_file_writer"):
            raise ValueError("setup_external_services may be called only once")
        cls._env = EnvManager(root_dir)
        cls._file_writer = FileWriter(cls._env.home())
        cls._perf_analyzer = PerfAnalyzer(cls._env.get("PAI_SETUP_ROOT"), enable_perf_analyzer)
        cls._logger = Logger(logs_dir, cls._perf_analyzer, enable_logger)

    @classmethod
    def finalize_services(cls):
        """
        Service objects may require to be finalized to perform some cleanup operations or print
        their results.
        """
        cls._env.finalize()
        cls._file_writer.finalize()
        cls._logger.finalize()
        cls._perf_analyzer.finalize()  # Has to be last

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

    def push_dependencies(self, dependency_dispatcher):
        """
        This method can be implemented by deriving classes.

        It allows to call methods of other steps through the DependencyDispatcher mechanism. Pushed
        dependencies can only transfer data to the receiving step.
        """
        pass

    def pull_dependencies(self, dependency_dispatcher):
        """
        This method can be implemented by deriving classes.

        It allows to call methods of other steps through the DependencyDispatcher mechanism. Pulled
        dependencies can only transfer data from the receiving step. All pulled dependencies are
        executed after all pushed dependencies are done.
        """
        pass

    def perform(self):
        """
        This method can be implemented by deriving classes.

        It is a main method performing actual operations done by the step. Example operations could
        be creating a file, setting up permissions, downloading a project. Not all steps have to
        implement this. Some of them may exist only to place dependencies on other steps. This method
        is called after all push_dependencies() and pull_dependencies() have executed and it can use
        the data transfered through dependencies.
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


# This is a fake step only needed to add packages required by the PaiSetup framework itself.
class FrameworkStep(Step):
    def __init__(self):
        super().__init__("Framework")

    def push_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_packages("flamegraph")
