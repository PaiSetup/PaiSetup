from steps.step import Step
from pathlib import Path
from utils.file_writer import FileType


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

    def perform(self):
        self._file_writer.write_section(
            ".profile",
            "Startup script to move python history",
            ['export PYTHONSTARTUP="$HOME/.config/python/pythonrc"'],
        )

        self._file_writer.write_lines(
            ".config/python/pythonrc",
            [
                "import readline",
                "readline.write_history_file = lambda *args: None",
            ],
            file_type=FileType.Python,
        )
