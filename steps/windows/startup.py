from steps.step import Step
from utils import command
from utils.log import log


class StartupStep(Step):
    def __init__(self):
        super().__init__("Startup")

    def perform(self):
        self._remove_scheduled_tasks()
        self._remove_services()

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
