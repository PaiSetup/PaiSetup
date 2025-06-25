import enum
import os
from pathlib import Path

from utils.os_function import *


class EnvConflict(Exception):
    pass


class EnvManager:
    def __init__(self):
        self._map = {}

        system = OperatingSystem.current()
        if system.is_windows():
            home = f"{os.environ['HOMEDRIVE']}{os.environ['HOMEPATH']}"
            user = os.environ["USERNAME"]
        elif system.is_linux():
            home = os.environ["HOME"]
            user = os.environ["USER"]

        self.set("HOME", home, setenv=False, is_path=True)
        self.set("USER", user, setenv=False, is_path=False)

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

    def finalize(self):
        pass
