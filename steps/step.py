from utils.log import log, LogIndent
import os
from utils.os_helpers import Pushd
from utils import command
from pathlib import Path
from utils.log import log, LogIndent


class Step:
    def __init__(self, name):
        self.name = name

    def get_required_packages(self):
        pass

    def perform(self, *args, **kwargs):
        log(f"Performing step: {self.name}")

        with LogIndent():
            self._perform_impl(*args, **kwargs)

    def _perform_impl(self, *args, **kwargs):
        raise NotImplementedError()


class SucklessSoftwareStep(Step):
    def __init__(self, name, url, revision, patches_dir):
        super().__init__(name)
        self.url = url
        self.revision = revision
        self.patches_dir = patches_dir

    def _perform_impl(self, root_build_dir):
        build_dir = root_build_dir / self.name
        log(f"Downloading {self.url} to {build_dir}")
        command.setup_git_repo(self.url, self.revision, build_dir)

        with Pushd(build_dir):
            diffs = list(Path(self.patches_dir).glob("*.diff"))
            log(f"Applying {len(diffs)} patches")
            with LogIndent():
                diffs.sort()
                for diff in diffs:
                    log(diff)
                    command.apply_patch(diff)

            log(f"Building and installing")
            command.run_command("sudo make install")
