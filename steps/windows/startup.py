from steps.step import Step
from utils import command
from utils.log import log
from utils.windows_registry import *


class StartupStep(Step):
    def __init__(self):
        super().__init__("Startup")

    def perform(self):
        self._remove_scheduled_tasks()
        self._remove_services()
        self._remove_startup_entries()

    def _remove_scheduled_tasks(self):
        tasks = [
            "XblGameSaveTaskLogon",
            "XblGameSaveTask",
            "Consolidator",
            "UsbCeip",
            "DmClient",
            "DmClientOnScenarioDownload",
        ]
        powershell_script = [f"Get-ScheduledTask {task} -ErrorAction SilentlyContinue | Disable-ScheduledTask | Out-Null" for task in tasks]
        log("Removing startup tasks")
        command.run_powershell_command(powershell_script)

    def _remove_services(self):
        services = [
            "dmwappushservice",
            "DiagTrack",
        ]
        powershell_script = [f'Stop-Service "{service}"; Set-Service "{service}" -StartupType Disabled' for service in services]
        log("Removing services")
        command.run_powershell_command(powershell_script)

    def _remove_startup_entries(self):
        # TODO these should ideally be added by other steps through dependency dispatcher
        log("Removing startup entries")
        self._remove_startup_entry("BCClipboard")
        self._remove_startup_entry("CCleaner Smart Cleaning")
        self._remove_startup_entry("Discord")
        self._remove_startup_entry("OneDrive")
        self._remove_startup_entry("Steam")
        self._remove_startup_entry("SunJavaUpdateSched")

    def _remove_startup_entry(self, name):
        for hive in [HKCU, HKLM]:
            for bitness in ["", "WOW6432Node\\"]:
                for subkey in [
                    "Run",
                    "RunOnce",
                    "Explorer\\StartupApproved\\Run",
                    "Explorer\\StartupApproved\\Run32",
                    "Explorer\\StartupApproved\\StartupFolder",
                ]:
                    key = rf"SOFTWARE\{bitness}Microsoft\Windows\CurrentVersion\{subkey}"
                    delete_registry_value(hive, key, name)
