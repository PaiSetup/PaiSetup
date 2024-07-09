from fnmatch import fnmatch

from Xlib import display
from Xlib.Xatom import RESOURCE_MANAGER, STRING


class XrdbException(Exception):
    pass


class Xrdb:
    def __init__(self):
        self._resources = self._load_resources()

    @staticmethod
    def _load_resources():
        xdisplay = display.Display()
        screen = xdisplay.screen()
        resource_man = screen.root.get_full_property(RESOURCE_MANAGER, STRING)
        raw_resources = resource_man.value.decode()

        mush = raw_resources.splitlines()
        resources = {}
        for line in mush:
            index, value = line.split(":\t")
            resources[index] = value
        return resources

    def get_resource(self, name):
        try:
            return self._resources[name]
        except KeyError:
            matching_resources = [res for res in self._resources.keys() if fnmatch(name, res)]
            if not matching_resources:
                raise XrdbException(f'Resource "{name}" not found.')

            matching_resources.sort(key=len, reverse=True)  # Could by n instead of nlogn, but I don't care.
            matching_resource = matching_resources[0]

            return self._resources[matching_resource]

    def get_all_resources(self):
        return self._resources.items()
