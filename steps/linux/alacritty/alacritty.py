from pathlib import Path

from steps.step import Step
from utils.services.file_writer import FileType


class AlacrittyStep(Step):
    def __init__(self):
        super().__init__("Alacritty")

    def register_env_variables(self):
        self._env.set("TERMINAL", "alacritty")
        self._env.set("TERMINAL_CMD", "alacritty -e")

    def push_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_packages("alacritty")

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
        self._file_writer.write_section(
            ".config/PaiSetup/env.sh",
            "Command for calling default terminal",
            [
                "export TERMINAL=alacritty",
                "export TERMINAL_CMD='alacritty -e'",
            ],
        )
