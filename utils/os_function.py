import platform
import sys
import enum

_current = None


class OperatingSystem(enum.Enum):
    Windows = "Windows"
    Linux = "Linux"

    @staticmethod
    def current():
        global _current
        if _current is None:
            system = platform.system()
            try:
                _current = OperatingSystem(system)
            except ValueError as e:
                raise NotImplementedError(f"Unsupported OS: {system}")
        return _current

    def is_windows(self):
        return self == OperatingSystem.Windows

    def is_linux(self):
        return self == OperatingSystem.Linux


def _os_function(implementation_os, func, frame):
    if OperatingSystem.current() == implementation_os:
        return func
    elif func.__name__ in frame.f_locals:
        return frame.f_locals[func.__name__]
    else:

        def _not_implemented(*args, **kwargs):
            raise NotImplementedError(f"Function {func.__name__} is not defined for {implementation_os}.")

        return _not_implemented


def linux_only(func):
    return _os_function(OperatingSystem.Linux, func, sys._getframe().f_back)


def windows_only(func):
    return _os_function(OperatingSystem.Windows, func, sys._getframe().f_back)


def require_windows():
    if OperatingSystem.current() != OperatingSystem.Windows:
        raise NotImplementedError("Windows is required")
