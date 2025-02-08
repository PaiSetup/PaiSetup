from pathlib import Path

from steps.step import Step
from utils.keybinding import KeyBinding
from utils.services.file_writer import FileType, LinePlacement


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
            "bpython",
            "tk",
        )
        dependency_dispatcher.add_keybindings(KeyBinding("p").mod().shift().executeShell("$TERMINAL python").desc("Python"))

    def perform(self):
        self._file_writer.write_section(
            ".config/PaiSetup/xinitrc_base",
            "Python path env needed for running PaiSetup scripts",
            [
                f'export PYTHONPATH="$PYTHONPATH:$PAI_SETUP_ROOT"',
            ],
            line_placement=LinePlacement.Env,
        )
        self._file_writer.write_section(
            ".config/PaiSetup/xinitrc_base",
            "Python config",
            [
                "export PYTHON_HISTORY=$XDG_DATA_HOME/python_history",
                'export PYTHONSTARTUP="$HOME/.config/python/pythonrc"',
            ],
        )

        self._file_writer.write_lines(
            ".config/python/pythonrc",
            [
                "import readline",
                "readline.write_history_file = lambda *args: None",
            ],
            file_type=FileType.Python,
        )
