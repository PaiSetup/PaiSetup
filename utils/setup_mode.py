import enum
from pathlib import Path


class SetupMode(enum.Enum):
    main = "main"  # My main machine
    extra = "extra"  # My extra machine, not a full setup
    normie = "normie"  # Setup for not very computer-literate people

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
