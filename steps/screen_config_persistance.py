from steps.step import Step
from utils import command
import os
from pathlib import Path
from utils.file_writer import FileType
from utils.log import log


class ScreenConfigPersistanceStep(Step):
    def __init__(self):
        super().__init__("ScreenConfigPersistance")

    def express_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_packages("autorandr")

        bgchecker_script = Path(__file__).parent / "check_unlocked_veracrypt.sh"
        dependency_dispatcher.register_bgchecker_script("autorandr -s latest --force >/dev/null", 120, delay=1)

    def perform(self):
        self._file_writer.write_section(
            ".config/LinuxSetup/xinitrc_base",
            "Reload screen config",
            ["(sleep 0.1 ; autorandr -l latest) &"],
        )
