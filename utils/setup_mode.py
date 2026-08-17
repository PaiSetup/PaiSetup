import importlib
from pathlib import Path

from utils.os_function import OperatingSystem


class SetupMode:
    """
    Base class for all setup modes. A setup mode describes a single kind of machine we want to
    configure - it defines the list of steps to perform on it. Concrete modes should derive from
    this class, implement its methods and be listed in the SETUP_MODES variable of the package
    they live in. See find_setup_modes() for details on how modes are discovered.
    """

    def get_name(self):
        """
        This method has to be implemented by deriving classes.

        It returns a unique, command line friendly name of this mode, which is used as a value
        for the --mode argument and stored in the .lastmode file.
        """
        raise NotImplementedError()

    def get_steps(self, args, root_dir, build_dir, secret_dir, install_packages):
        """
        This method has to be implemented by deriving classes.

        It returns a list of Step objects to perform in this mode.
        """
        raise NotImplementedError()

    def is_compatible(self):
        """
        This method can be implemented by deriving classes.

        It tells whether this mode can be used on the machine we're currently running on. It is
        used to validate the mode saved in .lastmode and to select the default mode.
        """
        return True

    def __str__(self):
        return self.get_name()

    @staticmethod
    def find_setup_modes():
        """
        Returns a dict mapping mode names to valid SetupMode objects. We look for setup modes in
        two kinds of locations:
        - OS-specific, e.g. steps/windows/__init__.py.
        - plugins, e.g. steps/plugins/my_plugin/__init__.py
        """

        # Prepare directories that can contain setup modes
        steps_dir = Path(__file__).parent.parent / "steps"
        os_dir_name = "windows" if OperatingSystem.current().is_windows() else "linux"
        package_dirs = [steps_dir / os_dir_name]
        package_dirs += [x for x in (steps_dir / "plugins").glob("*") if x.is_dir() and not x.name.startswith("__")]

        # Get setup modes from the directories
        setup_modes = {}
        all_mode_names = set()
        for package_dir in package_dirs:
            if not (package_dir / "__init__.py").is_file():
                continue

            package_name = ".".join(("steps",) + package_dir.relative_to(steps_dir).parts)
            package = importlib.import_module(package_name)

            mode_classes = getattr(package, "SETUP_MODES", None)
            if mode_classes is None:
                raise ValueError(f"Package {package_name} does not define a SETUP_MODES list")

            for mode_class in mode_classes:
                mode = mode_class()
                name = mode.get_name()

                # Names have to be unique even for the modes we filter out below, so that they
                # never silently shadow each other.
                if name in all_mode_names:
                    raise ValueError(f'Setup mode "{name}" defined by {package_name} is already defined elsewhere')
                all_mode_names.add(name)

                if mode.is_compatible():
                    setup_modes[name] = mode

        return setup_modes

    @staticmethod
    def retrieve_last_mode(root_dir, setup_modes):
        """
        Returns the mode saved in the .lastmode file, or a default one, if the file is missing or
        holds a mode we cannot use. May return None - see _get_default_mode().
        """
        lastmode_file = root_dir / ".lastmode"
        try:
            with open(lastmode_file, "r") as file:
                return setup_modes[file.readline().strip()]
        except (FileNotFoundError, KeyError):
            return SetupMode._get_default_mode(setup_modes)

    @staticmethod
    def _get_default_mode(setup_modes):
        """
        Returns the only mode usable on this machine or None, if there is no such mode or if there
        is more than one of them. In the latter case there is no reason to prefer any of them, so
        the user has to select one explicitly.
        """
        if len(setup_modes) == 1:
            return next(iter(setup_modes.values()))
        return None

    def save_last_mode(self, root_dir):
        lastmode_file = root_dir / ".lastmode"
        with open(lastmode_file, "w") as file:
            file.write(f"{self.get_name()}\n")
