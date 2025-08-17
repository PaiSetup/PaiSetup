import os
from pathlib import Path

from steps.linux.spieven.spieven import SpievenDisplayType
from steps.step import Step
from utils.command import *
from utils.services.file_writer import FileType


class UdiskieStep(Step):
    def __init__(self):
        super().__init__("Udiskie")

    def push_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_packages("udiskie")
        dependency_dispatcher.schedule_spieven_daemon("Udiskie", "udiskie", display_type=SpievenDisplayType.Headless)
