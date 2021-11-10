import subprocess
import shlex
import os
import utils.os_helpers
from pathlib import Path


class CommandError(Exception):
    def __init__(self, output):
        self.stdout = output[0].decode("ascii") if output[0] != None else "None"
        self.stderr = output[1].decode("ascii") if output[1] != None else "None"

    def __str__(self):
        print(f"stdout: {self.stdout}\n\nstderr: {self.stderr}")


def run_command(command, *, stdin=subprocess.PIPE):
    args = shlex.split(command)
    process = subprocess.Popen(args, stdin=stdin, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output = process.communicate()
    return_value = process.wait()

    if return_value != 0:
        raise CommandError(output)


def is_package_installed(package):
    try:
        run_command("pacman -Qi yay-git")
        return True
    except CommandError:
        return False


def setup_git_repo(url, revision, directory):
    git_dir = Path(directory) / ".git"
    if not git_dir.is_dir():
        run_command(f"git clone {url} {directory}")

    with utils.os_helpers.Pushd(directory):
        run_command(f"git reset {revision} --hard")
        run_command(f"git clean -fxd")
        run_command(f"sudo chmod ugo+rw {directory} -R")


def apply_patch(file):
    with open(file, "rb", 0) as file:
        run_command("patch", stdin=file)
        run_command("git add -A")
        run_command(f"git commit -m {file.name}")
