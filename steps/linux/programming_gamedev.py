from pathlib import Path

from steps.step import Step
from utils.services.file_writer import FileType


class ProgrammingGamedevStep(Step):
    def __init__(self):
        super().__init__("ProgrammingGamedev")

    def express_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_packages(
            "godot",
        )
