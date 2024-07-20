import os
import re
import shlex
import subprocess
from pathlib import Path

from utils.os_function import OperatingSystem, windows_only


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


class Stdin:
    def __init__(self, popen_arg, communicate_arg):
        self.popen_arg = popen_arg
        self.communicate_arg = communicate_arg

    @staticmethod
    def empty():
        return Stdin(None, None)

    @staticmethod
    def file(file_handle):
        return Stdin(file_handle, None)

    @staticmethod
    def string(content):
        return Stdin(subprocess.PIPE, bytes(content, "utf-8"))


class Stdout:
    def __init__(self, popen_arg, should_return):
        self.popen_arg = popen_arg
        self.should_return = should_return

    @staticmethod
    def ignore():
        return Stdout(subprocess.PIPE, False)  # We could use DEVNULL, but we need the outputs to throw errors

    @staticmethod
    def return_back():
        return Stdout(subprocess.PIPE, True)

    @staticmethod
    def print_to_console():
        return Stdout(None, False)

    @staticmethod
    def print_to_file(file_handle):
        return Stdout(file_handle, False)


# TODO add stdour and stderr returning
class Command:
    def __init__(self, process):
        self._process = process
        self._finished = False
        self._return_value = None

    def wait(self):
        if not self._finished:
            self._return_value = self._process.wait()
            self._finished = True

    def get_return_value(self):
        self._wait()
        return self._return_value


def run_command(command, *, shell=False, background=False, stdin=Stdin.empty(), stdout=Stdout.ignore(), stderr=Stdout.ignore()):
    if not shell and not OperatingSystem.current().is_windows():
        command = shlex.split(command)
    if background:
        if stdout.should_return or stderr.should_return:
            raise ValueError("Cannot run a background process which returns results.")
        if stdin.communicate_arg:
            raise ValueError("Cannot run a background process which gets stdin.")  # This may be to conservative...

    process = subprocess.Popen(command, shell=shell, stdin=stdin.popen_arg, stdout=stdout.popen_arg, stderr=stderr.popen_arg)
    if background:
        return Command(process)
    output = process.communicate(input=stdin.communicate_arg)
    return_value = process.wait()

    if return_value != 0:
        raise CommandError(output)

    result = []
    if stdout.should_return and output[0] != None:
        result.append(output[0].decode("utf-8"))
    if stderr.should_return and output[1] != None:
        result.append(output[1].decode("utf-8"))
    if len(result) == 2:
        return tuple(result)
    if len(result) == 1:
        return result[0]
    return None


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


@windows_only
def run_powershell_command(command, *args, **kwargs):
    if type(command) == list:
        command = ";".join(command)
    return run_command(["powershell", "-Command", command], *args, **kwargs)
