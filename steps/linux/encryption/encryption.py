from pathlib import Path

from steps.step import Step
from utils.keybinding import KeyBinding
from utils.services.file_writer import FileType


class EncryptionStep(Step):
    def __init__(self):
        super().__init__("Encryption")

    def push_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_packages(
            "cryptsetup",
            "cryptomator-bin",
            "veracrypt",
        )
        dependency_dispatcher.add_keybindings(
            KeyBinding("x").mod().shift().ctrl().executeShell("$PAI_SETUP_ROOT/steps/linux/encryption/mount_nice.sh").desc("Mount nice"),
            KeyBinding("r").mod().shift().ctrl().executeShell("$PAI_SETUP_ROOT/steps/linux/encryption/mount_receipts.sh").desc("Mount receipts"),
        )

        check_script = Path(__file__).parent / "check_unlocked_veracrypt.sh"
        dependency_dispatcher.register_periodic_check(check_script, 5, client_name="Veracrypt", multi_line=True)
