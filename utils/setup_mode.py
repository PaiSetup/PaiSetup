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

            if not lastmode._is_compatible():
                lastmode = SetupMode._get_default_mode()

            return lastmode

        except (FileNotFoundError, ValueError) as e:
            return SetupMode._get_default_mode()

    @staticmethod
    def _get_default_mode():
        if OperatingSystem.current().is_windows():
            return SetupMode.windows
        elif LinuxDistro.current().is_debian_like():
            return SetupMode.debian_casual
        elif LinuxDistro.current().is_arch_like():
            return SetupMode.arch
        else:
            raise ValueError("Unknown system")

    def _is_compatible(self):
        match self:
            case SetupMode.arch:
                return OperatingSystem.current().is_linux() and LinuxDistro.current().is_arch_like()
            case SetupMode.debian_casual | SetupMode.debian_work:
                return OperatingSystem.current().is_linux() and LinuxDistro.current().is_debian_like()
            case SetupMode.windows:
                return OperatingSystem.current().is_windows()
            case _:
                raise ValueError("Invalid SetupMode")

    def save_last_mode(self, root_dir):
        lastmode_file = root_dir / ".lastmode"
        with open(lastmode_file, "w") as file:
            file.write(f"{self.value}\n")
