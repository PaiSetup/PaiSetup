import enum
from pathlib import Path

from utils.os_function import LinuxDistro, OperatingSystem


class SetupMode(enum.Enum):
    arch = "arch"
    windows = "windows"
    windows_normie = "windows_normie"
    debian_casual = "debian_casual"
    debian_work = "debian_work"

    @staticmethod
    def retrieve_last_mode(root_dir):
        lastmode_file = root_dir / ".lastmode"
        try:
            with open(lastmode_file, "r") as file:
                lastmode = SetupMode(file.readline().strip())
        except (FileNotFoundError, ValueError) as e:
            if OperatingSystem.current().is_windows():
                lastmode = SetupMode.windows
            elif LinuxDistro.current().is_debian_like():
                lastmode = SetupMode.debian_casual
            else:
                lastmode = SetupMode.arch
        return lastmode

    def save_last_mode(self, root_dir):
        lastmode_file = root_dir / ".lastmode"
        with open(lastmode_file, "w") as file:
            file.write(f"{self.value}\n")
