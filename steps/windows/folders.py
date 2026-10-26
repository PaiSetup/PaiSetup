from pathlib import Path

from steps.step import Step
from utils.command import *
from utils.services.paths import KnownPath


# This step defines various paths used in our setup and publishes them in the known folders service. Some of them are
# default Windows system paths, like desktop or documents and some are just defined for the sake of this setup.
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
            self._folders[KnownPath.Root] = root_folder

        # Desktop, documents and public desktop directories will stay in default locations. We used to override them
        # with KnownFolders.exe from WindowsHandies, but it's not really worth it and it may complicate some things.
        self._folders[KnownPath.Desktop] = my_home_dir / "Desktop"
        self._folders[KnownPath.Documents] = my_home_dir / "Documents"
        self._folders[KnownPath.PublicDesktop] = public_home_dir / "Desktop"

        # Assign other folders. They will be under root_folder if specified. Otherwise, we'll have to put them in
        # various roughly acceptable places. It's not great.
        if root_folder is not None:
            self._folders[KnownPath.Programs] = root_folder / "Programs"
            self._folders[KnownPath.HwTools] = root_folder / "HwTools"
            self._folders[KnownPath.Games] = root_folder / "Games"
            self._folders[KnownPath.Work] = root_folder / "Projects"
            self._folders[KnownPath.Multimedia] = root_folder / "Multimedia"
        else:
            self._folders[KnownPath.Programs] = program_files_dir
            self._folders[KnownPath.HwTools] = program_files_dir
            self._folders[KnownPath.Games] = program_files_dir
            self._folders[KnownPath.Work] = my_home_dir / "Projects"
            self._folders[KnownPath.Multimedia] = my_home_dir / "Multimedia"

        # Register the paths to the Paths service.
        # TODO this also runs with --list_steps and --list_packages. Pass a special arg to skip creating directories then.
        for folder, path in self._folders.items():
            self._paths.set(folder, path)
            path.mkdir(parents=True, exist_ok=True)

    def push_dependencies(self, dependency_dispatcher):
        home = self._env.home()
        dependency_dispatcher.remove_folder_from_quick_access(home / "Desktop")
        dependency_dispatcher.remove_folder_from_quick_access(home / "Downloads")
        dependency_dispatcher.remove_folder_from_quick_access(home / "Documents")
        dependency_dispatcher.remove_folder_from_quick_access(home / "Pictures")
        dependency_dispatcher.remove_folder_from_quick_access(home / "Music")
        dependency_dispatcher.remove_folder_from_quick_access(home / "Videos")

        folders_to_add = [
            KnownPath.Desktop,
            KnownPath.Programs,
            KnownPath.Work,
        ]
        for folder in folders_to_add:
            if folder in self._folders:
                dependency_dispatcher.add_folder_to_quick_access(self._folders[folder])
        dependency_dispatcher.add_folder_to_quick_access(home)
