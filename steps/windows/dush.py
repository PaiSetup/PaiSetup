from steps.dush_base import DushStepBase
from utils.services.file_writer import FileType
from utils.services.paths import KnownPath


class DushStep(DushStepBase):
    def __init__(self):
        super().__init__("Dush")

    def _get_dush_dir(self):
        return self._paths.get(KnownPath.Root) / "Dush"

    def perform(self):
        dush_dir = self._get_dush_dir()
        projects_dir = self._paths.get(KnownPath.Work)

        self._download_dush(dush_dir)

        self._file_writer.write_section(
            ".bashrc",
            "Developer scripts",
            [
                f'export DUSH_PATH="{dush_dir}"',
                f'export DUSH_WORKSPACE="{projects_dir}"',
                f'export DUSH_ENABLE_AUTOLOAD="1"',
                ". $DUSH_PATH/dush/framework/frontend.bash",
                ". $DUSH_PATH/dush/projects/bashies/main.sh",
            ],
            file_type=FileType.Bash,
        )

        # TODO-WINDOWS: we cannot do this, because there are conflicts in PYTHONPATH between PaiSetup and Dush. We need to namespace it somehow.
        powershell_profile = self._paths.get(KnownPath.Documents) / "WindowsPowerShell\Microsoft.PowerShell_profile.ps1"
        self._file_writer.write_section(
            powershell_profile,
            "Developer scripts",
            [
                f'$env:PYTHONPATH = "{dush_dir};$env:PYTHONPATH"',
                f'$env:DUSH_WORKSPACE = "{projects_dir}"',
                f'$env:DUSH_PATH = "{dush_dir}"',
                "$env:DUSH_ENABLE_AUTOLOAD = $true",
                "Import-Module $env:DUSH_PATH/dush/projects/bashies/main.ps1",
            ],
        )
