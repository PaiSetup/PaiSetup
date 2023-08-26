from steps.step import Step
from pathlib import Path
from utils.services.file_writer import FileType
from utils.keybinding import KeyBinding


class ProgrammingPythonStep(Step):
    def __init__(self):
        super().__init__("Programming Python")

    def express_dependencies(self, dependency_dispatcher):
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
        dependency_dispatcher.add_keybindings(KeyBinding("p").mod().shift().executeShell("$TERMINAL python"))

    def perform(self):
        self._file_writer.write_section(
            ".config/PaiSetup/xinitrc_base",
            "Python config",
            [
                'export PYTHONSTARTUP="$HOME/.config/python/pythonrc"',
                f'export PYTHONPATH="$PYTHONPATH:{self._env.get("PAI_SETUP_ROOT")}"', # TODO use variable in the script
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
