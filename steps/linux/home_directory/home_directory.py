from steps.step import Step, dependency_listener
from pathlib import Path
import os
import itertools
from utils.log import log, LogIndent
from utils import command
from utils.services.file_writer import FileType


class HomeDirectoryStep(Step):
    def __init__(self, root_dir, is_main_machine):
        super().__init__("HomeDirectory")
        self._root_dir = root_dir
        self._homedir_whitelist = Path(__file__).parent / "homedir_whitelist"
        self._homedir_whitelisted_files = []

        self._xdg_defaults = {
            "XDG_CONFIG_HOME": ".config",
            "XDG_CACHE_HOME": ".cache",
            "XDG_DATA_HOME": ".local/share",
            "XDG_STATE_HOME": ".local/state",
        }
        self._xdg_removed = {
            "XDG_TEMPLATES_DIR": "Templates",
            "XDG_PUBLICSHARE_DIR": "Public",
            "XDG_DOCUMENTS_DIR": "Documents",
            "XDG_MUSIC_DIR": "Music",
            "XDG_PICTURES_DIR": "Pictures",
            "XDG_VIDEOS_DIR": "Videos",
        }
        self._xdg_renamed = {
            "XDG_DESKTOP_DIR": ("Desktop", "desktop"),
            "XDG_DOWNLOAD_DIR": ("Downloads", "downloads"),
        }
        self._xdg_custom = {  # These directories are non-standard. It's called XDG for convenience.
            "XDG_WORK_DIR": "work",
            "XDG_MULTIMEDIA_DIR": "multimedia",
            "XDG_MOUNTS_DIR": "mounts",
            "XDG_LOG_DIR": ".log",
        }
        if not is_main_machine:
            self._xdg_custom.pop("XDG_MULTIMEDIA_DIR")

    def express_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.set_folder_icon(self.get_xdg_dir("XDG_DESKTOP_DIR"), "desktop")
        dependency_dispatcher.set_folder_icon(self.get_xdg_dir("XDG_DOWNLOAD_DIR"), "downloads")
        dependency_dispatcher.set_folder_icon(self.get_xdg_dir("XDG_MOUNTS_DIR"), "mounts")
        dependency_dispatcher.set_folder_icon(self.get_xdg_dir("XDG_WORK_DIR"), "work")
        dependency_dispatcher.set_folder_icon(self._root_dir, "pai_setup")

        check_script = Path(__file__).parent / "setup_mount_dir.sh"
        dependency_dispatcher.register_periodic_check(check_script, 3)

        check_script = Path(__file__).parent / "verify_homedir.sh"
        dependency_dispatcher.register_periodic_check(check_script, 45, multi_line=True)

        multimedia_dir = self.get_xdg_dir("XDG_MULTIMEDIA_DIR", must_succeed=False)
        if multimedia_dir is not None:
            dependency_dispatcher.set_folder_icon(multimedia_dir, "multimedia")
            dependency_dispatcher.set_folder_icon(multimedia_dir / "avatars", "avatars")
            dependency_dispatcher.set_folder_icon(multimedia_dir / "freestyle_football", "football")
            dependency_dispatcher.set_folder_icon(multimedia_dir / "fret_saw", "fretsaw")
            dependency_dispatcher.set_folder_icon(multimedia_dir / "funny", "funny")
            dependency_dispatcher.set_folder_icon(multimedia_dir / "icons", "icons")
            dependency_dispatcher.set_folder_icon(multimedia_dir / "microscope", "microscope")
            dependency_dispatcher.set_folder_icon(multimedia_dir / "movies", "movies")
            dependency_dispatcher.set_folder_icon(multimedia_dir / "music", "music")
            dependency_dispatcher.set_folder_icon(multimedia_dir / "music_to_rate", "music")
            dependency_dispatcher.set_folder_icon(multimedia_dir / "tv_series", "tv_series")
            dependency_dispatcher.set_folder_icon(multimedia_dir / "wallpapers", "wallpapers")

    @dependency_listener
    def get_xdg_dir(self, name, must_succeed=True):
        result = self._xdg_defaults.get(name)
        if result is None:
            result = self._xdg_custom.get(name)
        if result is None:
            result = self._xdg_renamed.get(name)
            if result is not None:
                result = result[1]

        if result is not None:
            result = self._file_writer.resolve_path(result)
        elif must_succeed:
            raise ValueError(f"{name} is not an existing XDG directory name.")
        return result

    @dependency_listener
    def register_homedir_file(self, file, allow_multipart=False):
        filename = Path(file)
        if filename.is_absolute():
            try:
                filename = filename.relative_to("/home/maciej")
            except ValueError:
                log(f"ERROR: incorrect path passed: {file}")
                raise

        if len(filename.parts) != 1:
            if allow_multipart:
                filename = filename.parts[0]
            else:
                log(f"ERROR: incorrect path passed: {file}")
                raise ValueError()

        self._homedir_whitelisted_files.append(str(filename))

    def perform(self):
        self._create_directories()
        self._cleanup_existing_xdg_dirs()
        self._setup_xdg_paths()
        self._generate_files_whitelist()

        self._file_writer.write_section(
            ".profile",
            "Path to directory for working projects",
            ["export PROJECT_DIR=$HOME/work"],
        )

    def _create_directories(self):
        for xdg_dir in itertools.chain(self._xdg_defaults.values(), self._xdg_custom.values()):
            (self._env.home() / xdg_dir).mkdir(exist_ok=True)

        multimedia_dir = self.get_xdg_dir("XDG_MULTIMEDIA_DIR", must_succeed=False)
        if multimedia_dir is not None:
            # These directories are excluded from sync and we'll create them manually
            (multimedia_dir / "movies").mkdir(exist_ok=True)
            (multimedia_dir / "music").mkdir(exist_ok=True)
            (multimedia_dir / "music_to_rate").mkdir(exist_ok=True)
            (multimedia_dir / "tv_series").mkdir(exist_ok=True)

    def _cleanup_existing_xdg_dirs(self):
        with LogIndent("Making sure existing XDG dirs are ok"):
            # We renamed some default XDG dirs to different names, so we check if they are renamed in the filesystem
            for old, new in self._xdg_renamed.values():
                old_path = self._env.home() / old
                new_path = self._env.home() / new

                if new_path.exists():
                    if old_path.exists():
                        try:
                            old_path.rmdir()
                            log(f"{new_path}: OK ({old_path} existed, but it was removed)")
                        except OSError:
                            log(
                                f"{new_path}: WARNING - both {new_path} and {old_path} exist"
                            )  # TODO we want to keep the prefix before "WARNING". Add a new parameter to WarningHub.push?
                    else:
                        log(f"{new_path}: OK")
                else:
                    if old_path.exists():
                        old_path.rename(new_path)
                        log(f"{new_path}: OK (renamed from {old_path})")
                    else:
                        new_path.mkdir()
                        log(f"{new_path}: OK (created)")

            # We removed some default XDG dirs, so we check if they are truly gone
            for name in self._xdg_removed.values():
                path = self._env.home() / name
                if path.exists():
                    try:
                        path.rmdir()
                        log(f"{path}: OK (removed)")
                    except OSError:
                        log(f"{path}: WARNING - {path} exists, but should be removed")
                else:
                    log(f"{path}: OK")

            # Perform above removals on startup
            removals = [f"rmdir ~/{default_value} 2>/dev/null" for default_value in self._xdg_removed.values()]
            removals += [f"rmdir ~/{default_value} 2>/dev/null" for (default_value, _) in self._xdg_renamed.values()]
            self._file_writer.write_section(
                ".config/PaiSetup/xinitrc_base",
                "Remove unused directories in HOME",
                removals,
            )

    def _setup_xdg_paths(self):
        # Prepare our custom XDG dirs specification and generate some config files
        self._file_writer.write_lines(
            ".config/user-dirs.dirs",
            [
                "# Renamed dirs",
                'export XDG_DESKTOP_DIR="$HOME/desktop"',
                'export XDG_DOWNLOAD_DIR="$HOME/downloads"',
                "",
                "# From https://www.freedesktop.org/wiki/Software/xdg-user-dirs/:",
                '# "To disable a directory, point it to the homedir. If you delete it it will be recreated on the next login.',
                "# Removed dirs",
                'export XDG_TEMPLATES_DIR="$HOME"',
                'export XDG_PUBLICSHARE_DIR="$HOME"',
                'export XDG_DOCUMENTS_DIR="$HOME"',
                'export XDG_MUSIC_DIR="$HOME"',
                'export XDG_PICTURES_DIR="$HOME"',
                "",
                "# Default dirs",
                'export XDG_DATA_HOME="$HOME/.local/share"',
                'export XDG_CONFIG_HOME="$HOME/.config"',
                'export XDG_STATE_HOME="$HOME/.local/state"',
                'export XDG_CACHE_HOME="$HOME/.cache"',
            ],
        )

        # Set the variables in xinitrc too. We need it that early, so all GUI applications will have them loaded.
        self._file_writer.write_section(
            ".config/PaiSetup/xinitrc_base",
            "Load XDG variables",
            [". ~/.config/user-dirs.dirs"],
        )

        # Prevent resetting user-dirs.dirs file on startup.
        self._file_writer.write_lines(".config/user-dirs.conf", ["enabled=false"], file_type=FileType.ConfigFile)

    def _generate_files_whitelist(self):
        """
        We generate a file containing list of files that are allowed to be in home directory.
        If there are some other files, there will be an error reported by a periodic check.
        """

        # Add PaiSetup itself
        self.register_homedir_file(self._root_dir)

        # Add folders managed by this step
        for homedir_file in itertools.chain(
            self._xdg_defaults.values(),
            self._xdg_custom.values(),
            (x[1] for x in self._xdg_renamed.values()),
        ):
            self.register_homedir_file(homedir_file, allow_multipart=True)

        # Add some files which don't belong to any step and it's not worth creating new steps
        self.register_homedir_file(".ssh")  # TODO create SshStep and move it there? We could use it anyway, similar to Windows

        # Generate a file with all whitelisted files (including those registered by other steps)
        log("Generating homedir whitelist file")
        self._homedir_whitelisted_files = sorted(set(self._homedir_whitelisted_files))
        self._file_writer.write_lines(self._homedir_whitelist, self._homedir_whitelisted_files, file_type=FileType.ConfigFileNoComments)
