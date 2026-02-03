from enum import Enum, auto
from pathlib import Path

from steps.step import Step
from utils.command import *
from utils.dependency_dispatcher import pull_dependency_handler


class KnownFolder(Enum):
    Root = auto()  # Optional

    Desktop = auto()
    Documents = auto()
    PublicDesktop = auto()

    Programs = auto()
    HwTools = auto()
    Games = auto()
    Projects = auto()
    Multimedia = auto()
    VirtualMachines = auto()
    Dush = auto()


# This step serves as a source of knowledge for other steps about various paths used in our setup. Some of them are
# default Windows system paths, like desktop or documents and some are just defined for the sake of this setup. Other
# steps should query the paths in their pull_dependencies() phase, store them and use in perform() phase.
class FoldersStep(Step):
    def __init__(self, root_folder):
        super().__init__("Folders")
        self._folders = {}

        # Query some default Windows paths
        my_home_dir = self._env.home()
        public_home_dir = Path(self._env.get("PUBLIC"))
        program_files_dir = Path(self._env.get("programfiles"))

        # Add root folder if it's present
        if root_folder is not None:
            root_folder = Path(root_folder)
            self._folders[KnownFolder.Root] = root_folder

        # Desktop, documents and public desktop directories will stay in default locations. We used to override them
        # with KnownFolders.exe from WindowsHandies, but it's not really worth it and it may complicate some things.
        self._folders[KnownFolder.Desktop] = my_home_dir / "Desktop"
        self._folders[KnownFolder.Documents] = my_home_dir / "Documents"
        self._folders[KnownFolder.PublicDesktop] = public_home_dir / "Desktop"

        # Assign other folders. They will be under root_folder if specified. Otherwise, we'll have to put them in
        # various roughly acceptable places. It's not great.
        if root_folder is not None:
            self._folders[KnownFolder.Programs] = root_folder / "Programs"
            self._folders[KnownFolder.HwTools] = root_folder / "HwTools"
            self._folders[KnownFolder.Games] = root_folder / "Games"
            self._folders[KnownFolder.Projects] = root_folder / "Projects"
            self._folders[KnownFolder.Multimedia] = root_folder / "Multimedia"
            self._folders[KnownFolder.VirtualMachines] = root_folder / "VMs"
            self._folders[KnownFolder.Dush] = root_folder / "Dush"
        else:
            self._folders[KnownFolder.Programs] = default_program_files_dir
            self._folders[KnownFolder.HwTools] = default_program_files_dir
            self._folders[KnownFolder.Games] = default_program_files_dir
            self._folders[KnownFolder.Projects] = my_home_dir / "Projects"
            self._folders[KnownFolder.Multimedia] = my_home_dir / "Multimedia"
            self._folders[KnownFolder.VirtualMachines] = my_home_dir / "VMs"
            self._folders[KnownFolder.Dush] = my_home_dir / "Dush"

    @pull_dependency_handler
    def get_known_folders(self):
        # TODO change to get_known_folder(self, folder). Call mkdir there. Remove perform. Now we're dependent on order of steps.
        return self._folders

    def push_dependencies(self, dependency_dispatcher):
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
        ]
        for folder in folders_to_add:
            if folder in self._folders:
                dependency_dispatcher.add_folder_to_quick_access(self._folders[folder])
        dependency_dispatcher.add_folder_to_quick_access(home)

    def perform(self):
        for _, path in self._folders.items():
            path.mkdir(parents=True, exist_ok=True)
