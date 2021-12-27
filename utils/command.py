import subprocess
import shlex
import os
import utils.os_helpers
from pathlib import Path
import re


class CommandError(Exception):
    def __init__(self, output):
        self.stdout = self.stderr = None
        if output is not None:
            if output[0] is not None:
                self.stdout = output[0].decode("utf-8")
            if output[1] is not None:
                self.stderr = output[1].decode("utf-8")

    def __str__(self):
        print(f"stdout: {self.stdout}\n\nstderr: {self.stderr}")


def run_command(command, *, shell=False, stdin=subprocess.PIPE, return_stdout=False, print_stdout=False):
    if not shell:
        command = shlex.split(command)

    if return_stdout and print_stdout:
        raise ValueError("Returning and printing stdout at the same time is not supported")
    stdout = subprocess.PIPE
    if print_stdout:
        stdout = None

    process = subprocess.Popen(command, shell=shell, stdin=stdin, stdout=stdout, stderr=stdout)
    output = process.communicate()
    return_value = process.wait()

    if return_value != 0:
        raise CommandError(output)

    if return_stdout and output[0] != None:
        return output[0].decode("utf-8")


def get_missing_packages(arg):
    known_package_groups = ["base-devel"]

    packages = [p for p in arg if p not in known_package_groups]
    package_groups = [p for p in arg if p in known_package_groups]

    # Try to get info on packages and package groups. Pacman will print a line to stderr for each
    # package that isn't installed.
    missing = []
    if packages:
        packages = " ".join(packages)
        try:
            run_command(f"pacman -Qi {packages}")
        except CommandError as e:
            missing += e.stderr.splitlines()
    if package_groups:
        package_groups = " ".join(package_groups)
        try:
            run_command(f"pacman -Qg {package_groups}")
        except CommandError as e:
            missing += e.stderr.splitlines()

    # Extract package name from the line
    missing = [re.search("'([^']+)'", x).group(1) for x in missing]
    return missing


def setup_git_repo(url, revision, directory):
    git_dir = Path(directory) / ".git"
    if not git_dir.is_dir():
        run_command(f"git clone {url} {directory}")

    with utils.os_helpers.Pushd(directory):
        run_command(f"git reset {revision} --hard")
        run_command(f"git clean -fxd")
        run_command(f"sudo chmod ugo+rw {directory} -R")


def setup_git_repo_on_latest_commit(url, directory, pull_latest, branch_name="master"):
    git_dir = Path(directory) / ".git"
    if not git_dir.is_dir():
        run_command(f"git clone {url} {directory}")

    with utils.os_helpers.Pushd(directory):
        run_command(f"git checkout {branch_name} -f")
        if pull_latest:
            run_command(f"git pull")


def apply_patch(file):
    with open(file, "rb", 0) as file:
        run_command("patch", stdin=file)
        run_command(f"git commit -am {file.name}")


def create_executable_script(file_name, lines):
    path = Path("/") / "usr" / "local" / "bin" / file_name
    lines = ["#!/bin/sh"] + lines
    lines = "\n".join(lines)

    run_command(f'echo "{lines}" | sudo tee {path} >/dev/null', shell=True)
    run_command(f"sudo chmod 755 {path}")
