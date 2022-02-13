from steps.step import Step
from pathlib import Path
from steps.dotfiles import FileType


class EncryptionStep(Step):
    def __init__(self):
        super().__init__("Encryption", has_action=False)

    def express_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_packages(
            "cryptsetup",
            "cryptomator-bin",
        )
        dependency_dispatcher.add_dotfile_lines(
            ".config/sxhkd/sxhkdrc",
            [
                "super + control + shift + x",
                "    $LINUX_SETUP_ROOT/steps/encryption/mount_nice.sh",
                "",
                "super + control + shift + r",
                "    $LINUX_SETUP_ROOT/steps/encryption/mount_receipts.sh",
                "",
            ],
            file_type=FileType.ConfigFile,
        )
