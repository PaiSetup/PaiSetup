from enum import Enum, auto
from pathlib import Path

from utils.os_function import OperatingSystem


class KnownPath(Enum):
    # Available on all systems
    Home = auto()
    PaiSetup = auto()
    BuildDir = auto()
    SecretDir = auto()
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


class KnownPathQueriedTooEarly(Exception):
    pass


class Paths:
    def __init__(self, home, pai_setup_root):
        self._paths = {}
        self._steps_initialized = False
        self.set(KnownPath.Home, home)
        self.set(KnownPath.PaiSetup, pai_setup_root)
        self.set(KnownPath.BuildDir, Path(pai_setup_root) / "build")
        self.set(KnownPath.SecretDir, Path(pai_setup_root) / "secret")

    def set(self, known_path, path):
        if known_path in self._paths:
            raise KnownPathConflict(f"Duplicate path: {known_path.name}")
        self._paths[known_path] = Path(path)

    def mark_steps_initialized(self):
        self._steps_initialized = True

    def get(self, known_path, required=True):
        # Steps set paths in their __init__(), so querying a path in __init__() of another step would depend
        # on the order in which the steps are constructed.
        # Paths set on construction are always safe to query.
        if not self._steps_initialized and known_path not in (KnownPath.Home, KnownPath.PaiSetup, KnownPath.BuildDir, KnownPath.SecretDir):
            raise KnownPathQueriedTooEarly(f"Known path {known_path.name} cannot be queried before all steps are initialized")

        path = self._paths.get(known_path)
        if path is None and required:
            raise KeyError(f"Known path {known_path.name} is not set")
        return path

    def home(self):
        return self.get(KnownPath.Home)

    def finalize(self):
        pass
