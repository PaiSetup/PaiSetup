from steps.step import Step
from utils.command import *


class GitStep(Step):
    def __init__(self):
        super().__init__("Git")

    def push_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_packages("git")

    def perform(self):
        self._logger.log(f"Setting git user")
        run_command("git config --global user.name MaciejDziuban")
        run_command("git config --global user.email dziuban.maciej@gmail.com")
