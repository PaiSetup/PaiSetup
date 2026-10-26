import os
from pathlib import Path

from steps.step import Step
from utils.command import *
from utils.os_function import LinuxDistro
from utils.services.file_writer import FileType
from utils.services.paths import KnownPath


class GitStep(Step):
    def __init__(self):
        super().__init__("Git")
        self._user_name = "MaciejDziuban"
        self._user_email = "dziuban.maciej@gmail.com"

    def push_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_packages("git")

    def perform(self):
        gitconfig_dir = self._paths.get(KnownPath.ConfigHome) / "git"
        gitconfig_path = gitconfig_dir / "config"
        self._logger.log(f"Creating {gitconfig_path} file")
        gitconfig_dir.mkdir(parents=True, exist_ok=True)
        gitconfig_path.touch(exist_ok=True)

        self._logger.log(f"Setting git user to {self._user_email}")
        run_command(f'git config --global user.name "{self._user_name}"')
        run_command(f"git config --global user.email {self._user_email}")

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
