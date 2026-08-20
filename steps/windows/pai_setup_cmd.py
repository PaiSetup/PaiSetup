from steps.step import Step
from steps.windows.folders import KnownFolder


class PaiSetupCmdStep(Step):
    def __init__(self, root_dir):
        super().__init__("PaiSetupCmd")
        self._root_dir = root_dir

    def pull_dependencies(self, dependency_dispatcher):
        known_folders = dependency_dispatcher.get_known_folders()
        self._desktop_dir = known_folders[KnownFolder.Desktop]

    def perform(self):
        lines = [
            f'$pai_setup_path = "{self._root_dir}"',
            'Start-Process "powershell" -ArgumentList "-NoExit","-Command","Set-Location \'$pai_setup_path\'; Write-Host \'HINT: run python ./setup.py\'" -Verb RunAs',
        ]
        ps1_path = self._desktop_dir / "PaiSetupCmd.ps1"
        self._logger.log(f"Creating PaiSetupCmd shortcut at {ps1_path}")
        ps1_path.write_text("\n".join(lines) + "\n")
