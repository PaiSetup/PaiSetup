import os
import re
import shlex
import subprocess
from pathlib import Path

from utils.os_function import OperatingSystem, windows_only


class CommandError(Exception):
    def __init__(self, stdout, stderr):
        self.stdout = stdout
        self._stderr = stderr

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


class Command:
    def __init__(self, process):
        self._process = process
        self._return_value = None
        self.stdout = None
        self.stderr = None

    def wait(self):
        if self._return_value is None:
            self._return_value = self._process.wait()
        return self._return_value


def run_command(command, *, shell=False, background=False, stdin=Stdin.empty(), stdout=Stdout.ignore(), stderr=Stdout.ignore()):
    if not shell and not OperatingSystem.current().is_windows():
        command = shlex.split(command)
    if background:
        if stdout.should_return or stderr.should_return:
            raise ValueError("Cannot run a background process which returns results.")
        if stdin.communicate_arg:
            raise ValueError("Cannot run a background process which gets stdin.")  # This may be to conservative...

    # Launch process
    process = subprocess.Popen(command, shell=shell, stdin=stdin.popen_arg, stdout=stdout.popen_arg, stderr=stderr.popen_arg)
    result = Command(process)

    # Early return if it's a background process
    if background:
        return result

    # Process output
    (stdout_data, stderr_data) = process.communicate(input=stdin.communicate_arg)
    if stdout_data is not None:
        stdout_data = stdout_data.decode("utf-8")
    if stderr_data is not None:
        stderr_data = stderr_data.decode("utf-8")
    if stdout.should_return:
        result.stdout = stdout_data
        result.stderr = stderr_data

    # Wait for completion and check result
    return_value = result.wait()
    if return_value != 0:
        raise CommandError(stdout_data, stderr_data)

    # Return the command object
    return result


@windows_only
def run_powershell_command(command, *args, **kwargs):
    if type(command) == list:
        command = ";".join(command)
    return run_command(["powershell", "-Command", command], *args, **kwargs)
