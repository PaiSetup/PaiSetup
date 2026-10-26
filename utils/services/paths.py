from enum import Enum, auto
from pathlib import Path

from utils.os_function import OperatingSystem


class KnownPath(Enum):
    # Available on all systems
    Home = auto()
    PaiSetup = auto()
    Desktop = auto()
    Work = auto()
    Multimedia = auto()

    if OperatingSystem.current().is_windows():
        Root = auto()
        Documents = auto()
        PublicDesktop = auto()
        Programs = auto()
        HwTools = auto()
        Games = auto()

    if OperatingSystem.current().is_linux():
        ConfigHome = auto()
        CacheHome = auto()
        DataHome = auto()
        StateHome = auto()
        Downloads = auto()
        Log = auto()


class KnownPathConflict(Exception):
    pass


class Paths:
    def __init__(self, home, pai_setup_root):
        self._paths = {}
        self.set(KnownPath.Home, home)
        self.set(KnownPath.PaiSetup, pai_setup_root)

    def set(self, known_path, path):
        if known_path in self._paths:
            raise KnownPathConflict(f"Duplicate path: {known_path.name}")
        self._paths[known_path] = Path(path)

    def get(self, known_path, required=True):
        path = self._paths.get(known_path)
        if path is None and required:
            raise KeyError(f"Known path {known_path.name} is not set")
        return path

    def finalize(self):
        pass
