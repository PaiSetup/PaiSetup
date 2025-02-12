from steps.step import Step
from utils.command import *
from utils.dependency_dispatcher import push_dependency_handler
from utils.windows.shortcut import create_shortcut
from utils.windows.windows_registry import *


class StartupStep(Step):
    def __init__(self):
        super().__init__("Startup")
        self._entries_to_add = []
        self._entries_to_remove = []

    def perform(self):
        self.remove_startup_entry("OneDrive")

        self._remove_scheduled_tasks()
        self._remove_services()
        self._remove_startup_entries()
        self._add_startup_entries()

    def pull_dependencies(self, dependency_dispatcher):
        self._entries_to_remove = dependency_dispatcher.get_generated_startup_entries()

    @push_dependency_handler
    def add_startup_entry(self, name, script, as_admin):
        self._entries_to_add.append((name, script, as_admin))

    @push_dependency_handler
    def remove_startup_entry(self, name):
        self._entries_to_remove.append(name)

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
        self._logger.log("Removing startup tasks")
        run_powershell_command(powershell_script)

    def _remove_services(self):
        services = [
            "dmwappushservice",
            "DiagTrack",
        ]
        powershell_script = [f'Stop-Service "{service}"; Set-Service "{service}" -StartupType Disabled' for service in services]
        self._logger.log("Removing services")
        run_powershell_command(powershell_script)

    def _remove_startup_entries(self):
        self._logger.log("Removing startup entries")

        hives = [HKCU, HKLM]
        startup_subkeys = [
            "Run",
            "RunOnce",
            "Explorer\\StartupApproved\\Run",
            "Explorer\\StartupApproved\\Run32",
            "Explorer\\StartupApproved\\StartupFolder",
        ]
        bitness_subkeys = ["", "WOW6432Node\\"]
        for name in self._entries_to_remove:
            for hive in hives:
                for bitness_subkey in bitness_subkeys:
                    for startup_subkey in startup_subkeys:
                        key = rf"SOFTWARE\{bitness_subkey}Microsoft\Windows\CurrentVersion\{startup_subkey}"
                        delete_registry_value(hive, key, name)

    def _add_startup_entries(self):
        self._logger.log("Adding startup entries")

        # We could add entries to HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Run, but it's impossible to
        # run as admin without UAC. Shortcuts with SLDF_RUNAS_USER somehow don't require UAC during startup.
        # Although, they still show it when run manually.
        for name, script, as_admin in self._entries_to_add:
            shortcut_name = f"PaiSetup.{name}"
            shortcut_path = self._env.home() / rf"AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\{shortcut_name}"
            create_shortcut(shortcut_path, script, as_admin=as_admin)
