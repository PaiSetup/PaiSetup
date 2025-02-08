from pathlib import Path

from steps.step import Step
from steps.windows.folders import KnownFolder
from utils import external_project as ext
from utils.command import *


class IconsStep(Step):
    def __init__(self):
        super().__init__("Icons")
        self._icons_dir = Path(__file__).parent / "icons"
        self._merge_commands = False

    def push_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_packages("windows-handies")

        known_folders = dependency_dispatcher.get_known_folders()
        self._root_folder = known_folders.get(KnownFolder.Root)
        self._multimedia_folder = known_folders.get(KnownFolder.Multimedia)
        self._programs_folder = known_folders.get(KnownFolder.Programs)
        self._hw_tools_folder = known_folders.get(KnownFolder.HwTools)

    def perform(self):
        self.download_icons()
        self.setup_icons()

    def download_icons(self):
        self._logger.log("Downloading icons")
        ext.download_github_zip("PaiSetup", "WindowsIcons", self._icons_dir, False)

    def setup_icons(self):
        # Gather commands to execute
        icon_commands = []
        if self._root_folder:
            icon_commands.append(f'Iconfigure.exe -y -f -l "{self._icons_dir}" -d "{self._root_folder}"')
        if self._multimedia_folder:
            icon_commands.append(f'Iconfigure.exe -y -f -l "{self._icons_dir}" -d "{self._multimedia_folder}"')
        if self._programs_folder or self._hw_tools_folder:
            icon_command = f'Iconfigure.exe -y -f -l "{self._icons_dir}" -r'
            if self._programs_folder:
                icon_command += f' -d "{self._programs_folder}"'
            if self._hw_tools_folder:
                icon_command += f' -d "{self._hw_tools_folder}"'
            icon_commands.append(icon_command)

        # Execute commands
        self._logger.log("Setting up icons")
        if self._merge_commands:
            run_powershell_command(icon_commands)
        else:
            for icon_command in icon_commands:
                run_powershell_command([icon_command])
