from steps.step import Step
from utils.command import *


class RaspberryPiStep(Step):
    def __init__(self):
        super().__init__("RaspberryPi")

    def express_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_packages(
            "putty",
            "screen",
            "rpi-imager-bin",
            "thonny",
            "python-paramiko",
        )

    def perform(self):
        (self._env.home() / ".config/putty").mkdir(exist_ok=True)
        self._setup_permissions()

    def _setup_permissions(self):
        self._logger.log("Setting permissions")
        run_command(f"sudo usermod -aG uucp {self._env.get('USER')}")
