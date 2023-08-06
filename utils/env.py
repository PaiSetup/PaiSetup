import os
from utils.os_function import *
from pathlib import Path


class EnvConflict(Exception):
    pass


class EnvManager:
    def __init__(self, root_dir):
        self._map = {}

        system = OperatingSystem.current()
        if system.is_windows():
            home = os.environ["HOMEPATH"]
            user = os.environ["USERNAME"]
            display = None
        elif system.is_linux():
            home = os.environ["HOME"]
            user = os.environ["USER"]
            display = os.environ["DISPLAY"] if "DISPLAY" in os.environ else None

        self.set("HOME", home, setenv=False, is_path=True)
        self.set("USER", user, setenv=False, is_path=False)
        if display:
            self.set("DISPLAY", os.environ["DISPLAY"], setenv=False, is_path=False)
        else:
            self.set("DISPLAY", "", setenv=False, is_path=False)
        self.set("PAI_SETUP_ROOT", root_dir, is_path=True)

    def set(self, name, value, setenv=True, is_path=False, force=False):
        if not force and name in self._map:
            raise EnvConflict(f"Duplicate name: {name}")
        if is_path:
            value = Path(value)
        self._map[name] = value
        if setenv:
            os.environ[name] = str(value)

    def get(self, name):
        if name in self._map:
            return self._map[name]
        else:
            return os.environ[name]

    def home(self):
        return self.get("HOME")
