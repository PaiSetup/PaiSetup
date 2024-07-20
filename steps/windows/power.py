from steps.step import Step
from utils.command import *


class PowerStep(Step):
    def __init__(self):
        super().__init__("Power")

    def perform(self):
        self._logger.log("Setting standby timeout")
        powershell_command = [
            "Powercfg /Change standby-timeout-ac 0",
            "Powercfg /Change monitor-timeout-ac 120",
        ]
        run_powershell_command(powershell_command)
