import os
from pathlib import Path


class EnvConflict(Exception):
    pass


class EnvManager:
    def __init__(self):
        self._map = {}
        self.set("HOME", os.environ["HOME"], setenv=False, is_path=True)
        self.set("USER", os.environ["USER"], setenv=False, is_path=False)

    def set(self, name, value, setenv=True, is_path=False):
        if name in self._map:
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
