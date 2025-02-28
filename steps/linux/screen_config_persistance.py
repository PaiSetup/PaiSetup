import os
from pathlib import Path

from steps.step import Step
from utils.command import *
from utils.services.file_writer import FileType


class ScreenConfigPersistanceStep(Step):
    def __init__(self):
        super().__init__("ScreenConfigPersistance")

    def push_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_packages("autorandr")
        dependency_dispatcher.register_periodic_check(
            "autorandr -s latest --force >/dev/null", 120, delay_in_seconds=120, shell=True, client_name="Autorandr"
        )

    def perform(self):
        self._file_writer.write_section(
            ".config/PaiSetup/xinitrc_base",
            "Reload screen config",
            ["(sleep 0.1 ; autorandr -l latest) &"],
        )
