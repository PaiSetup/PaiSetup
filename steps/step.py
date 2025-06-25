import enum

from utils.services.file_writer import FileType, LinePlacement


class Step:
    """
    Base class for all steps of setting up the working environment. A step is a logical part
    of the whole process, which can be filtered out by its name. Concrete steps should
    derive from this class and implement one or more of its methods.
    """

    def __init__(self, name):
        self.name = name
        self._enabled = True

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
    def __init__(self, root_dir):
        super().__init__("Framework")
        self._root_dir = root_dir

    def push_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_packages("flamegraph")

    def register_env_variables(self):
        self._env.set("PAI_SETUP_ROOT", self._root_dir, is_path=True)

    def perform(self):
        self._logger.get_log_dir().mkdir(parents=True, exist_ok=True)
        self._setup_constant_envs()

    def _setup_constant_envs(self):
        self._file_writer.write_section(
            ".config/PaiSetup/env.sh",
            "Envs needed for PaiSetup framework",
            [
                f"export PAI_SETUP_ROOT={self._root_dir}",
                f'export PYTHONPATH="$PYTHONPATH:$PAI_SETUP_ROOT"',
            ],
        )

        self._file_writer.write_section(
            ".profile",
            "Load environment variables",
            [". ~/.config/PaiSetup/env.sh"],
            line_placement=LinePlacement.Env,
        )
        self._file_writer.write_section(
            ".config/PaiSetup/xinitrc_base",
            "Load environment variables",
            [". ~/.config/PaiSetup/env.sh"],
            line_placement=LinePlacement.Env,
        )
        self._file_writer.write_section(
            ".bashrc",
            "Load environment variables",
            [". ~/.config/PaiSetup/env.sh"],
            line_placement=LinePlacement.Env,
            file_type=FileType.Bash,
        )
