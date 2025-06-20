import os
from pathlib import Path

from steps.step import Step
from utils.command import *
from utils.os_function import LinuxDistro
from utils.services.file_writer import FileType


class GitStep(Step):
    def __init__(self):
        super().__init__("Git")

    def push_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_packages("git")

    def perform(self):
        gitconfig_dir = self._env.home() / ".config/git"
        gitconfig_path = gitconfig_dir / "config"
        self._logger.log(f"Creating {gitconfig_path} file")
        gitconfig_dir.mkdir(parents=True, exist_ok=True)
        gitconfig_path.touch(exist_ok=True)

        self._logger.log(f"Setting git user")
        run_command("git config --global user.name MaciejDziuban")
        run_command("git config --global user.email dziuban.maciej@gmail.com")

        self._logger.log(f"Adding git completion to .bashrc")
        completion_file = "/usr/share/git/completion/git-completion.bash"
        if LinuxDistro.current().is_debian_like():
            completion_file = "/usr/share/bash-completion/completions/git"
        self._file_writer.write_section(
            ".bashrc",
            "Enable git commands completion",
            [f". {completion_file}"],
            file_type=FileType.Bash,
        )
