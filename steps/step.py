from utils.log import log, LogIndent
import os
from utils.os_helpers import Pushd
from utils import command
from pathlib import Path
from utils.log import log, LogIndent
import multiprocessing



class Step:
    def __init__(self, name):
        self.name = name

    def register_as_dependency_listener(self, dependency_dispatcher):
        pass

    def express_dependencies(self, dependency_dispatcher):
        pass

    def perform(self):
        log(f"Performing step: {self.name}")

        with LogIndent():
            self._perform_impl()

    def _perform_impl(self):
        raise NotImplementedError()

    def _compile_remote_project(
        self,
        build_dir,
        url,
        revision,
        patches_dir=None,
        setup_repo=False,
        cmake=False,
        has_submodules=False,
        multicore_compilation=True,
        cmake_args="",
    ):
        if setup_repo:
            log(f"Downloading {url} to {build_dir}")
            command.setup_git_repo(url, revision, build_dir, has_submodules=has_submodules)
        else:
            log(f"Skipping repo setup for {build_dir}")

        with Pushd(build_dir) as current_dir:
            if setup_repo and patches_dir:
                diffs = list(Path(patches_dir).glob("*.diff"))
                log(f"Applying {len(diffs)} patches")
                with LogIndent():
                    diffs.sort()
                    for diff in diffs:
                        log(diff)
                        command.apply_patch(diff)

            if cmake:
                (build_dir / "build").mkdir(parents=False, exist_ok=True)
                current_dir.cd("build")
                log("Running CMake")
                command.run_command(f"cmake .. {cmake_args}")

            log(f"Building and installing")
            if multicore_compilation:
                cores = multiprocessing.cpu_count()
                multicore_arg = f"-j{cores}"
            else:
                multicore_arg = ""
            command.run_command(f"sudo make install {multicore_arg}")
