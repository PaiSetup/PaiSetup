from utils import command
from pathlib import Path
from utils.os_helpers import Pushd
from utils.log import log, LogIndent
import multiprocessing


def apply_patch(file):
    with open(file, "rb", 0) as file:
        command.run_command("patch", stdin=file)
        command.run_command(f"git commit -am {file.name}")


def download(
    url,
    revision,
    directory,
    *,
    has_submodules=False,
    clean=False,
    fetch=False,
    chmod_needed=True, # TODO make this false by default
):
    log(f"Downloading {url} to {directory}")

    # Download code
    git_dir = Path(directory) / ".git"
    clone_needed = not git_dir.is_dir()
    if clone_needed:
        command.run_command(f"git clone {url} {directory}")

    # Go to directory and configure project
    with Pushd(directory):
        if clone_needed and has_submodules:
            command.run_command(f"git submodule init")
            command.run_command(f"git submodule update")

        if fetch and not clone_needed:
            command.run_command("git fetch --prune")

        if clean:
            command.run_command(f"git reset --hard")
            command.run_command(f"git clean -fxd --exclude build")

        command.run_command(f"git checkout {revision}")

        if chmod_needed:
            command.run_command(f"sudo chmod ugo+rw {directory} -R")


def cmake(
    project_dir,
    *,
    build_dir_name="build",
    cmake_args="",
):
    build_dir = project_dir / build_dir_name
    build_dir.mkdir(parents=False, exist_ok=True)
    with Pushd(build_dir):
        log(f"Configure CMake project: {project_dir}")
        command.run_command(f"cmake .. {cmake_args}")


def make(
    build_dir,
    *,
    patches_dir=None,
    target="install",
):
    with Pushd(build_dir):
        # Apply patches
        if patches_dir:
            diffs = list(Path(patches_dir).glob("*.diff"))
            log(f"Applying {len(diffs)} patches")
            with LogIndent():
                diffs.sort()
                for diff in diffs:
                    log(diff)
                    apply_patch(diff)

        # Get thread count
        cores = multiprocessing.cpu_count()
        multicore_arg = f"-j{cores}"

        # Compile
        log(f"Building and installing with {cores} threads")
        command.run_command(f"sudo make {target} {multicore_arg}")
