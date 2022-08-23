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


def get_missing_packages(arg, known_package_groups):
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
