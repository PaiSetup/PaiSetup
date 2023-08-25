from steps.step import Step
from utils import command


class TimeStep(Step):
    def __init__(self):
        super().__init__("Time")

    def perform(self):
        powershell_command = [
            'Set-TimeZone "Central European Standard Time"',
        ]
        command.run_powershell_command(powershell_command)
