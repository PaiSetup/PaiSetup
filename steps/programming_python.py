from steps.step import Step
from pathlib import Path
from steps.dotfiles import FileType


class ProgrammingPythonStep(Step):
    def __init__(self):
        super().__init__("Programming Python")

    def express_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_dotfile_lines(
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
