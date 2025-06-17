import os
from pathlib import Path

from steps.step import Step
from utils.command import *
from utils.services.file_writer import FileType


class UdiskieStep(Step):
    def __init__(self):
        super().__init__("Udiskie")

    def push_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_packages("udiskie")
        dependency_dispatcher.register_periodic_daemon_check("[a-zA-Z/]+python[23]? [a-zA-Z/_]+udiskie", "udiskie")

    def perform(self):
        self._file_writer.write_section(
            ".config/PaiSetup/xinitrc_base",
            "Automounting daemon",
            ["udiskie &"],
        )
