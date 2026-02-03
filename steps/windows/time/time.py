from pathlib import Path

from steps.step import Step
from utils.command import *
from utils.windows.windows_registry import *


class TimeStep(Step):
    def __init__(self):
        super().__init__("Time")
        self._sync_time_script_path = Path(__file__).parent / "sync_time.ps1"

    def push_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_startup_entry("sync_time", self._sync_time_script_path, as_admin=True)

    def _set_time_zone(self):
        powershell_command = [
            'Set-TimeZone "Central European Standard Time"',
        ]
        run_powershell_command(powershell_command)

    def _set_time_format(self):
        set_registry_value_string(HKCU, r"Control Panel\International", "sDate", "-")
        set_registry_value_string(HKCU, r"Control Panel\International", "sShortDate", "yyyy-MM-dd")
        set_registry_value_string(HKCU, r"Control Panel\International", "sTimeFormat", "HH:mm:ss")
        set_registry_value_string(HKCU, r"Control Panel\International", "sShortTime", "HH:mm")
        set_registry_value_string(HKCU, r"Control Panel\International", "iDate", "2")
        set_registry_value_string(HKCU, r"Control Panel\International", "iFirstDayOfWeek", "0")
        set_registry_value_string(HKCU, r"Control Panel\International", "iTime", "1")
        set_registry_value_string(HKCU, r"Control Panel\International", "iTLZero", "1")

    def perform(self):
        self._set_time_zone()
        self._set_time_format()
