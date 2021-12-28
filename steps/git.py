from steps.step import Step
from utils import command
import os
from pathlib import Path


class GitStep(Step):
    def __init__(self):
        super().__init__("Git")

    def setup_required_packages(self, packages_step):
        packages_step.add_packages("git")

    def _perform_impl(self):
        gitconfig_dir = Path(os.environ["HOME"]) / ".config" / "git"
        gitconfig_path = gitconfig_dir / "config"
        gitconfig_dir.mkdir(parents=True, exist_ok=True)
        gitconfig_path.touch(exist_ok=True)

        command.run_command("git config --global user.name MaciejDziuban")
        command.run_command("git config --global user.email dziuban.maciej@gmail.com")
