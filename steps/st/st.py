from steps.step import Step
from pathlib import Path


class StStep(Step):
    def __init__(self, root_build_dir, setup_repo):
        super().__init__("st")
        self.root_build_dir = root_build_dir
        self.setup_repo = setup_repo

    def _perform_impl(self):
        self._compile_remote_project(
            self.root_build_dir / "st",
            "https://git.suckless.org/st",
            "0.8.2",
            Path(__file__).parent,
            self.setup_repo,
        )
