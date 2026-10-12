from steps.step import Step
from utils.command import *


class GitStep(Step):
    def __init__(self):
        super().__init__("Git")
        self._user_name = "MaciejDziuban"
        self._user_email = "dziuban.maciej@gmail.com"

    def push_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_packages("git")

    def perform(self):
        self._logger.log(f"Setting git user to {self._user_email}")
        run_command(f'git config --global user.name "{self._user_name}"')
        run_command(f"git config --global user.email {self._user_email}")
