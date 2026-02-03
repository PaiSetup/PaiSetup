from steps.dush_base import DushStepBase
from steps.windows.folders import KnownFolder


class DushStep(DushStepBase):
    def __init__(self, fetch_git):
        super().__init__("Dush", fetch_git)

    def pull_dependencies(self, dependency_dispatcher):
        known_folders = dependency_dispatcher.get_known_folders()

        self._projects_dir = known_folders[KnownFolder.Projects]
        self._documents_dir = known_folders[KnownFolder.Documents]
        self._dush_dir = known_folders[KnownFolder.Dush]

        self.setup_dush_root_dir(self._dush_dir)

    def perform(self):
        super().perform()
        self._file_writer.write_section(
            ".profile",
            "Developer scripts",
            [
                f'export DUSH_PATH="{self._dush_root_dir}"',
                f'export DUSH_WORKSPACE="{self._projects_dir}"',
                f'export DUSH_ENABLE_AUTOLOAD="1"',
                ". $DUSH_PATH/framework/frontend.bash",
                ". $DUSH_PATH/projects/bashies/main.sh",
            ],
        )

        powershell_profile = self._documents_dir / "WindowsPowerShell\Microsoft.PowerShell_profile.ps1"
        self._file_writer.write_section(
            powershell_profile,
            "Developer scripts",
            [
                f'$env:PYTHONPATH = "{self._dush_dir};$env:PYTHONPATH"',
                f'$env:DUSH_WORKSPACE = "{self._projects_dir}"',
                f'$env:DUSH_PATH = "{self._dush_dir}"',
                "$env:DUSH_ENABLE_AUTOLOAD = $true",
                "Import-Module $env:DUSH_PATH/projects/bashies/main.ps1",
            ],
        )
