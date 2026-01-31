from enum import Enum, auto
from pathlib import Path

from steps.step import Step
from utils.command import *
from utils.dependency_dispatcher import pull_dependency_handler


class KnownFolder(Enum):
    Root = auto()
    Desktop = auto()
    Documents = auto()
    Games = auto()
    HwTools = auto()
    Multimedia = auto()
    Programs = auto()
    Projects = auto()
    Dush = auto()
    VirtualMachines = auto()
    PublicDesktop = auto()


class FoldersStep(Step):
    def __init__(
        self,
        separate_hw_tools=True,
        include_multimedia=True,
        include_games=True,
        include_projects=True,
        include_vms=True,
    ):
        super().__init__("Folders")
        self._folders = {}

        # Setup root folder
        root_folder = Path(r"C:\develop")
        self._folders[KnownFolder.Root] = root_folder

        # Add system locations
        self._folders[KnownFolder.Desktop] = self._env.home() / "Desktop"
        self._folders[KnownFolder.Documents] = self._env.home() / "Documents"
        self._folders[KnownFolder.Programs] = Path(self._env.get("programfiles"))
        self._folders[KnownFolder.PublicDesktop] = Path(self._env.get("PUBLIC")) / "Desktop"

        # Add custom locations
        if include_games:
            self._folders[KnownFolder.Games] = root_folder / "Games"
        if include_multimedia:
            self._folders[KnownFolder.Multimedia] = root_folder / "Multimedia"
        if include_projects:
            self._folders[KnownFolder.Projects] = root_folder / "Projects"
        if include_vms:
            self._folders[KnownFolder.VirtualMachines] = root_folder / "VMs"
        self._folders[KnownFolder.HwTools] = root_folder / "HwTools" if separate_hw_tools else self._folders[KnownFolder.Programs]
        self._folders[KnownFolder.Dush] = root_folder / "Dush"

    @pull_dependency_handler
    def get_known_folders(self):
        return self._folders

    def push_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_packages("windows-handies")

        home = self._env.home()
        dependency_dispatcher.remove_folder_from_quick_access(home / "Desktop")
        dependency_dispatcher.remove_folder_from_quick_access(home / "Downloads")
        dependency_dispatcher.remove_folder_from_quick_access(home / "Documents")
        dependency_dispatcher.remove_folder_from_quick_access(home / "Pictures")
        dependency_dispatcher.remove_folder_from_quick_access(home / "Music")
        dependency_dispatcher.remove_folder_from_quick_access(home / "Videos")

        folders_to_add = [
            KnownFolder.Desktop,
            KnownFolder.Programs,
            KnownFolder.Projects,
            KnownFolder.Multimedia,
        ]
        for folder in folders_to_add:
            if folder in self._folders:
                dependency_dispatcher.add_folder_to_quick_access(self._folders[folder])
        dependency_dispatcher.add_folder_to_quick_access(home)

    def perform(self):
        for _, path in self._folders.items():
            path.mkdir(parents=True, exist_ok=True)
