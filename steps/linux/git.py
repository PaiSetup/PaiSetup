from steps.step import Step
from utils import command
import os
from pathlib import Path
from utils.services.file_writer import FileType


class GitStep(Step):
    def __init__(self):
        super().__init__("Git")

    def express_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_packages("git")

    def perform(self):
        gitconfig_dir = self._env.home() / ".config/git"
        gitconfig_path = gitconfig_dir / "config"
        self._logger.log(f"Creating {gitconfig_path} file")
        gitconfig_dir.mkdir(parents=True, exist_ok=True)
        gitconfig_path.touch(exist_ok=True)

        self._logger.log(f"Setting git user")
        command.run_command("git config --global user.name MaciejDziuban")
        command.run_command("git config --global user.email dziuban.maciej@gmail.com")

        self._logger.log(f"Adding git completion to .bashrc")
        self._file_writer.write_section(
            ".bashrc",
            "Enable git commands completion",
            [". /usr/share/git/completion/git-completion.bash"],
            file_type=FileType.Bash,
        )
