from steps.step import Step
from utils.command import *


class TimeStep(Step):
    def __init__(self):
        super().__init__("Time")

    def perform(self):
        powershell_command = [
            'Set-TimeZone "Central European Standard Time"',
        ]
        run_powershell_command(powershell_command)
