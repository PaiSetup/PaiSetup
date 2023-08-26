from steps.step import Step
from pathlib import Path
from utils.services.file_writer import FileType
from utils.keybinding import KeyBinding


class ProgrammingGamedevStep(Step):
    def __init__(self):
        super().__init__("ProgrammingGamedev")

    def express_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_packages(
            "godot",
        )
