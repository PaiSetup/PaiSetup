from steps.step import Step
from utils import command
from utils.log import log


class PowerStep(Step):
    def __init__(self):
        super().__init__("Power")

    def perform(self):
        log("Setting standby timeout")
        powershell_command = [
            "Powercfg /Change standby-timeout-ac 0",
            "Powercfg /Change monitor-timeout-ac 120",
        ]
        command.run_powershell_command(powershell_command)
