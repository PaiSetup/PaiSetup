import multiprocessing
import shutil
import tempfile
from pathlib import Path

from utils.command import *
from utils.os_function import OperatingSystem
from utils.os_helpers import Pushd


def apply_patch(file):
    with open(file, "rb", 0) as file:
        run_command("patch", stdin=Stdin.file(file))
        run_command(f"git commit -am {file.name}")


def should_build(full, binaries):
    if full:
        return True
    return any((shutil.which(x) is None for x in binaries))


def download(
    url,
    revision,
    directory,
    *,
    logger,
    has_submodules=False,
    clean=False,
    fetch=False,
    chmod_needed=False,
):
    logger.log(f"Downloading {url} to {directory}")

    # Download code
    git_dir = Path(directory) / ".git"
    clone_needed = not git_dir.is_dir()
    if clone_needed:
        run_command(f"git clone {url} {directory}")

    # Go to directory and configure project
    with Pushd(directory):
        if clone_needed and has_submodules:
            run_command(f"git submodule init")
            run_command(f"git submodule update")

        if fetch and not clone_needed:
            run_command("git fetch --prune")

        if clean:
            run_command(f"git reset --hard")
            run_command(f"git clean -fxd --exclude build")

        run_command(f"git checkout {revision}")

        if chmod_needed:
            run_command(f"sudo chmod ugo+rw {directory} -R")


def cmake(
    project_dir,
    *,
    logger,
    build_dir_name="build",
    cmake_args="",
):
    build_dir = project_dir / build_dir_name
    build_dir.mkdir(parents=False, exist_ok=True)
    with Pushd(build_dir):
        logger.log(f"Configure CMake project: {project_dir}")
        run_command(f"cmake .. {cmake_args}")


def make(
    build_dir,
    *,
    logger,
    patches_dir=None,
    target="install",
):
    with Pushd(build_dir):
        # Apply patches
        if patches_dir:
            diffs = list(Path(patches_dir).glob("*.diff"))
            logger.log(f"Applying {len(diffs)} patches")
            with logger.indent():
                diffs.sort()
                for diff in diffs:
                    logger.log(str(diff))
                    apply_patch(diff)

        # Get thread count
        cores = multiprocessing.cpu_count()
        multicore_arg = f"-j{cores}"

        # Compile
        logger.log(f"Building and installing with {cores} threads")
        run_command(f"sudo make {target} {multicore_arg}")


def download_github_zip(user, repo, dst_dir, re_download=False):
    # Handle the case when there destination path is already present
    if dst_dir.is_dir():
        if re_download:
            shutil.rmtree(dst_dir)
        else:
            return
    elif dst_dir.exists():
        raise FileExistsError(f"{dst_dir} already exists, but it's not a directory")

    with tempfile.NamedTemporaryFile(suffix=".zip") as zipfile:
        # Download the zip package
        url = f"https://github.com/{user}/{repo}/archive/refs/heads/master.zip"
        if OperatingSystem.current().is_windows():
            zipfile.close()  # This prevents "File is already used by another process" error
            url = [
                "$ProgressPreference = 'SilentlyContinue'",
                f'Invoke-WebRequest "{url}" -OutFile "{zipfile.name}"',
            ]
            run_powershell_command(url)
        else:
            download_command = f'wget "{url}" -O "{output_file}"'
            run_command(download_command)

        dst_parent_dir = dst_dir.parent
        with Pushd(dst_parent_dir):
            # Unzip to the parent of desired destination directory
            if OperatingSystem.current().is_windows():
                unzip_command = [
                    "$ProgressPreference = 'SilentlyContinue'",
                    f'Expand-Archive {zipfile.name} -DestinationPath "."',
                ]
                run_powershell_command(unzip_command)
            else:
                unzip_command = f"unzip {zipfile.name}"
                run_command(unzip_command)

            # In the zip there is one folder called <ProjectName>-<BranchName>. Rename it to the name of desired destination director
            Path(f"{repo}-master").rename(dst_dir)
