import enum
from pathlib import Path


class SetupMode(enum.Enum):
    main = "main"  # TODO rename to "arch"
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
            lastmode = SetupMode.main
        return lastmode

    def save_last_mode(self, root_dir):
        lastmode_file = root_dir / ".lastmode"
        with open(lastmode_file, "w") as file:
            file.write(f"{self.value}\n")
