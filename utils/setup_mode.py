import enum
from pathlib import Path


class SetupMode(enum.Enum):
    main = "main"  # My main machine
    normie = "normie"  # Setup for beginners
    normie_plus = "normie_plus"  # Setup for beginners + additional stuff like tiling WMs, so I can comfortably use it as well

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
