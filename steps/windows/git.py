from steps.step import Step
from utils import command
import os
from pathlib import Path
from utils.file_writer import FileType
from utils.log import log


class GitStep(Step):
    def __init__(self):
        super().__init__("Git")

    def express_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_packages("git")

    def perform(self):
        log(f"Setting git user")
        command.run_command("git config --global user.name MaciejDziuban")
        command.run_command("git config --global user.email dziuban.maciej@gmail.com")
