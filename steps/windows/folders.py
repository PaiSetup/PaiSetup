from steps.step import Step
from enum import Enum, auto
from pathlib import Path
from utils import command


class KnownFolder(Enum):
    Root = auto()
    Desktop = auto()
    Documents = auto()
    Games = auto()
    HwTools = auto()
    Multimedia = auto()
    Programs = auto()
    Projects = auto()
    Scripts = auto()
    Toolbar = auto()
    VirtualMachines = auto()


class FoldersStep(Step):
    def __init__(
        self,
        root_folder,
        override_programs=True,
        separate_hw_tools=True,
        include_multimedia=True,
        include_games=True,
        include_projects=True,
    ):
        super().__init__("Folders")
        root_folder = Path(root_folder)
        self._folders = {
            KnownFolder.Root: root_folder,
            KnownFolder.Desktop: root_folder / "Desktop",
            KnownFolder.Documents: root_folder / "Documents",
            KnownFolder.Games: root_folder / "Games",
            KnownFolder.HwTools: root_folder / "HwTools",
            KnownFolder.Multimedia: root_folder / "Multimedia",
            KnownFolder.Programs: root_folder / "Programs",
            KnownFolder.Projects: root_folder / "Projects",
            KnownFolder.Scripts: root_folder / "Scripts",
            KnownFolder.Toolbar: root_folder / "Toolbar",
            KnownFolder.VirtualMachines: root_folder / "VirtualMachines",
        }
        if not override_programs:
            program_files_dir = self._env.get("programfiles")
            self._folders[KnownFolder.Programs] = program_files_dir
            self._folders[KnownFolder.HwTools] = program_files_dir
        if not separate_hw_tools:
            self._folders[KnownFolder.HwTools] = self._folders[KnownFolder.Programs]
        if not include_multimedia:
            self._folders.pop(KnownFolder.Multimedia)
        if not include_games:
            self._folders.pop(KnownFolder.Games)
        if not include_projects:
            self._folders.pop(KnownFolder.Projects)

    def get_known_folders(self, **kwargs):
        return self._folders

    def register_as_dependency_listener(self, dependency_dispatcher):
        dependency_dispatcher.register_listener(self.get_known_folders)

    def express_dependencies(self, dependency_dispatcher):
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
        self._setup_known_folders()
        self._create_folders()

    def _setup_known_folders(self):
        command.run_command(f"KnownFolders.exe -f Desktop -p {self._folders[KnownFolder.Desktop]} -m -r")
        # TODO it is difficult to move Documents. Investigate it.
        # command.run_command(f"KnownFolders.exe -f Documents -p {self._folders[KnownFolder.Documents]} -m -r")

    def _create_folders(self):
        for _, path in self._folders.items():
            path.mkdir(parents=True, exist_ok=True)
