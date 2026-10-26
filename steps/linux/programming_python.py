from pathlib import Path

from steps.step import Step
from utils.keybinding import KeyBinding
from utils.services.file_writer import FileType, LinePlacement
from utils.services.paths import KnownPath


class ProgrammingPythonStep(Step):
    def __init__(self):
        super().__init__("Programming Python")

    def push_dependencies(self, dependency_dispatcher):
        self._file_writer.write_lines(
            ".config/bpython/config",
            [
                "[general]",
                "arg_spec = False",
            ],
            file_type=FileType.ConfigFile,
        )
        dependency_dispatcher.add_packages(
            "python",
            "python-pip",
            "python-matplotlib",
            "bpython",
            "tk",
        )
        dependency_dispatcher.add_keybindings(KeyBinding("p").mod().shift().executeShell("$TERMINAL_CMD python").desc("Python"))

        dependency_dispatcher.set_env("Python paths", "PYTHON_HISTORY", self._paths.get(KnownPath.DataHome) / "python_history")
        dependency_dispatcher.set_env("Python paths", "PYTHONSTARTUP", f"{self._env.home()}/.config/python/pythonrc")

    def perform(self):
        self._file_writer.write_lines(
            ".config/python/pythonrc",
            [
                "import readline",
                "readline.write_history_file = lambda *args: None",
            ],
            file_type=FileType.Python,
        )
