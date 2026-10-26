from pathlib import Path

from steps.step import Step
from utils.services.file_writer import FileType


class AlacrittyStep(Step):
    def __init__(self):
        super().__init__("Alacritty")

    def push_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_packages("alacritty")
        dependency_dispatcher.set_env("Command for calling default terminal", "TERMINAL", "alacritty")
        dependency_dispatcher.set_env("Command for calling default terminal", "TERMINAL_CMD", "alacritty -e")

    def perform(self):
        current_step_dir = Path(__file__).parent
        self._file_writer.write_symlink(
            src=current_step_dir / "alacritty.toml",
            link=".config/alacritty/alacritty.toml",
        )

        self._file_writer.write_section(
            ".profile",
            "Alacritty alias",
            [
                "alias al=alacritty",
            ],
        )
