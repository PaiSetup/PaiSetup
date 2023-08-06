from steps.step import Step
from enum import Enum, auto
from pathlib import Path


class KnownFolder(Enum):
    Desktop = auto()
    Games = auto()
    HwTools = auto()
    Multimedia = auto()
    Programs = auto()
    Projects = auto()
    Scripts = auto()
    Toolbar = auto()
    VirtualMachines = auto()


class FoldersStep(Step):
    def __init__(self, root_folder, override_programs=True, separate_hw_tools=True, include_multimedia=True, include_games=True):
        super().__init__("Folders")
        root_folder = Path(root_folder)
        self._folders = {
            KnownFolder.Desktop: root_folder / "Desktop",
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

    def get_known_folders(self, **kwargs):
        return self._folders

    def register_as_dependency_listener(self, dependency_dispatcher):
        dependency_dispatcher.register_listener(self.get_known_folders)

    def perform(self):
        self._create_folders()

    def _create_folders(self):
        for _, path in self._folders.items():
            path.mkdir(parents=True, exist_ok=True)