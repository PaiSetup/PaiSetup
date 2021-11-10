from steps.step import Step
from pathlib import Path


class StStep(Step):
    def __init__(self):
        super().__init__("st")

    def _perform_impl(self, root_build_dir):
        self._compile_remote_project(
            root_build_dir / "st",
            "https://git.suckless.org/st",
            "0.8.2",
            Path(__file__).parent,
            True,
        )
