from steps.step import Step
from utils import command


class GitStep(Step):
    def __init__(self):
        super().__init__("git")

    def _perform_impl(self):
        command.run_command("git config --global user.name MaciejDziuban")
        command.run_command("git config --global user.email dziuban.maciej@gmail.com")
        command.run_command('git config --global url."ssh://git@github.com".insteadOf https://github.com')
