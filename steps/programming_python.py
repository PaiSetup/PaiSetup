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
