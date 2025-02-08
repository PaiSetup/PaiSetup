from pathlib import Path

from steps.step import Step
from utils.command import *


class TimeStep(Step):
    def __init__(self):
        super().__init__("Time")
        self._sync_time_script_path = Path(__file__).parent / "sync_time.ps1"

    def express_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_startup_entry("sync_time", self._sync_time_script_path, as_admin=True)

    def perform(self):
        powershell_command = [
            'Set-TimeZone "Central European Standard Time"',
        ]
        run_powershell_command(powershell_command)
