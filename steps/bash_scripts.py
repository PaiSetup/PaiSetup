from steps.step import Step
from utils import command
from utils.log import log
import os
from pathlib import Path


class BashScriptsStep(Step):
    def __init__(self, setup_repo, pull_latest):
        super().__init__("BashScripts")
        self.setup_repo = setup_repo
        self.pull_latest = pull_latest
        self.scripts_dir = scripts_dir = Path(os.environ["HOME"]) / "Scripts"

    def _perform_impl(self):
        if self.setup_repo:
            log(f"Pulling latest version of scripts to {self.scripts_dir}")
            command.setup_git_repo_on_latest_commit(
                "https://github.com/InternalMD/Scripts.git", self.scripts_dir, self.pull_latest
            )
        else:
            log(f"Skipping repo setup for {self.scripts_dir}")

    def express_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_dotfile_section(
            ".profile",
            "Convenience scripts",
            [
                f'export SCRIPTS_PATH="{self.scripts_dir}/BashUtils"',
                ". $SCRIPTS_PATH/load_functions.sh",
            ],
        )
