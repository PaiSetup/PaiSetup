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
        dependency_dispatcher.register_periodic_check("autorandr -s latest --force >/dev/null", 120, delay=120, shell=True)

    def perform(self):
        self._file_writer.write_section(
            ".config/LinuxSetup/xinitrc_base",
            "Reload screen config",
            ["(sleep 0.1 ; autorandr -l latest) &"],
        )
