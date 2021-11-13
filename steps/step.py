from utils.log import log, LogIndent
import os
from utils.os_helpers import Pushd
from utils import command
from pathlib import Path
from utils.log import log, LogIndent


class Step:
    def __init__(self, name):
        self.name = name

    def setup_required_packages(self, packages_step):
        pass

    def setup_required_dotfiles(self, dotfiles_step):
        pass

    def perform(self):
        log(f"Performing step: {self.name}")

        with LogIndent():
            self._perform_impl()

    def _perform_impl(self):
        raise NotImplementedError()

    def _compile_remote_project(self, build_dir, url, revision, patches_dir, setup_repo):
        if setup_repo:
            log(f"Downloading {url} to {build_dir}")
            command.setup_git_repo(url, revision, build_dir)
        else:
            log(f"Skipping repo setup for {build_dir}")

        with Pushd(build_dir):
            if setup_repo:
                diffs = list(Path(patches_dir).glob("*.diff"))
                log(f"Applying {len(diffs)} patches")
                with LogIndent():
                    diffs.sort()
                    for diff in diffs:
                        log(diff)
                        command.apply_patch(diff)

            log(f"Building and installing")
            command.run_command("sudo make install")
