from pathlib import Path

import utils.external_project as ext
from steps.linux.spieven.spieven import SpievenDisplayType
from steps.step import Step
from utils.keybinding import KeyBinding
from utils.services.file_writer import FileType
from utils.services.paths import KnownPath


class EncryptionStep(Step):
    def __init__(self):
        super().__init__("Encryption")
        self._current_step_dir = Path(__file__).parent

    def push_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_packages(
            "cryptsetup",
            "cryptomator-bin",
            "veracrypt",
            "rclone",
        )
        dependency_dispatcher.add_keybindings(
            KeyBinding("x").mod().shift().ctrl().executeShell("$PAI_SETUP_ROOT/steps/linux/encryption/mount_nice.sh").desc("Mount nice"),
            KeyBinding("z").mod().shift().ctrl().executeShell("$PAI_SETUP_ROOT/steps/linux/encryption/mount_receipts.sh").desc("Mount receipts"),
            KeyBinding("b").mod().shift().ctrl().executeShell("$PAI_SETUP_ROOT/steps/linux/encryption/mount_blz.sh").desc("Mount blz"),
        )

        check_script = self._current_step_dir / "check_unlocked_veracrypt.sh"
        dependency_dispatcher.schedule_spieven_periodic_check("Veracrypt", check_script, display_type=SpievenDisplayType.Headless, delay_ms=5_000)

        multimedia_unlock_script = self._current_step_dir / "mount_multimedia.sh"
        dependency_dispatcher.schedule_spieven_daemon("MountMultimedia", multimedia_unlock_script, display_type=SpievenDisplayType.Headless)

    def perform(self):
        self._download_cryptomator_cli()

    def _download_cryptomator_cli(self):
        with self._logger.indent("Setting up cryptomator-cli"):
            version = "0.6.2"
            dst_dir = self._paths.get(KnownPath.BuildDir) / f"cryptomator-cli-{version}"
            downloaded = ext.download_github_release(
                "cryptomator",
                "cli",
                dst_dir,
                version,
                f"cryptomator-cli-{version}-linux-x64.zip",
                re_download=False,
            )
            if downloaded:
                self._logger.log("Downloaded, setting executable symlink")
                self._file_writer.write_symlink_executable(dst_dir / "cryptomator-cli/bin/cryptomator-cli", "cryptomator-cli")
            else:
                self._logger.log("Already setup")
