from steps.step import Step
from pathlib import Path
from utils.keybinding import KeyBinding
from utils.file_writer import FileType


class EncryptionStep(Step):
    def __init__(self):
        super().__init__("Encryption")

    def express_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_packages(
            "cryptsetup",
            "cryptomator-bin",
        )
        dependency_dispatcher.add_keybindings(
            KeyBinding("x").mod().shift().ctrl().executeShell("$PAI_SETUP_ROOT/steps/encryption/mount_nice.sh"),
            KeyBinding("r").mod().shift().ctrl().executeShell("$PAI_SETUP_ROOT/steps/encryption/mount_receipts.sh"),
        )

        check_script = Path(__file__).parent / "check_unlocked_veracrypt.sh"
        dependency_dispatcher.register_periodic_check(check_script, 5, client_name="Veracrypt")
