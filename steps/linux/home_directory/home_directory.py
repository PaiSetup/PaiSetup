import itertools
import os
from pathlib import Path

from steps.linux.spieven.spieven import SpievenDisplayType
from steps.step import Step
from utils.command import *
from utils.dependency_dispatcher import push_dependency_handler
from utils.services.file_writer import FileType
from utils.services.paths import KnownPath


class HomeDirectoryStep(Step):
    def __init__(self, has_multimedia_dir):
        super().__init__("HomeDirectory")
        self._homedir_whitelisted_files = []

        # Prepare all XDG dirs. Some of them we leave at default, some we remove, rename or add.
        # They may need different handling in some places, so we keep them in different vars.
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
            "XDG_MOUNTS_DIR": "mounts",
            "XDG_LOG_DIR": ".log",
        }

        # Register the paths to the Paths service.
        self._paths.set(KnownPath.ConfigHome, self._get_xdg_dir("XDG_CONFIG_HOME"))
        self._paths.set(KnownPath.CacheHome, self._get_xdg_dir("XDG_CACHE_HOME"))
        self._paths.set(KnownPath.DataHome, self._get_xdg_dir("XDG_DATA_HOME"))
        self._paths.set(KnownPath.StateHome, self._get_xdg_dir("XDG_STATE_HOME"))
        self._paths.set(KnownPath.Desktop, self._get_xdg_dir("XDG_DESKTOP_DIR"))
        self._paths.set(KnownPath.Downloads, self._get_xdg_dir("XDG_DOWNLOAD_DIR"))
        self._paths.set(KnownPath.Work, self._get_xdg_dir("XDG_WORK_DIR"))
        self._paths.set(KnownPath.Log, self._get_xdg_dir("XDG_LOG_DIR"))
        self._homedir_whitelist = self._get_xdg_dir("XDG_CONFIG_HOME") / "PaiSetup/homedir_whitelist"

        # Multimedia directory is optional.
        if has_multimedia_dir:
            self._xdg_custom["XDG_MULTIMEDIA_DIR"] = "multimedia"
            self._paths.set(KnownPath.Multimedia, self._get_xdg_dir("XDG_MULTIMEDIA_DIR"))

    def register_env_variables(self):
        for name, path in self._xdg_defaults.items():
            self._env.set(name, self._paths.home() / path, is_path=True)

    def push_dependencies(self, dependency_dispatcher):
        for name, path in self._xdg_defaults.items():
            dependency_dispatcher.set_env("XDG variables", name, self._paths.home() / path)
        for name, (_, path) in self._xdg_renamed.items():
            dependency_dispatcher.set_env("XDG variables", name, self._paths.home() / path)
        for name in self._xdg_removed:
            dependency_dispatcher.set_env("XDG variables", name, self._paths.home())

        dependency_dispatcher.set_folder_icon(self._get_xdg_dir("XDG_DESKTOP_DIR"), "desktop")
        dependency_dispatcher.set_folder_icon(self._get_xdg_dir("XDG_DOWNLOAD_DIR"), "downloads")
        dependency_dispatcher.set_folder_icon(self._get_xdg_dir("XDG_MOUNTS_DIR"), "mounts")
        dependency_dispatcher.set_folder_icon(self._get_xdg_dir("XDG_WORK_DIR"), "work")
        dependency_dispatcher.set_folder_icon(self._paths.get(KnownPath.PaiSetup), "pai_setup")

        check_script = Path(__file__).parent / "setup_mount_dir.sh"
        dependency_dispatcher.schedule_spieven_periodic_action(
            "SetupMountDir", check_script, display_type=SpievenDisplayType.Headless, delay_ms=3_000
        )

        check_script = Path(__file__).parent / "verify_homedir.sh"
        dependency_dispatcher.schedule_spieven_periodic_check(
            "VerifyHomedir",
            check_script,
            display_type=SpievenDisplayType.Headless,
            delay_ms=45_000,
        )

        multimedia_dir = self._get_xdg_dir("XDG_MULTIMEDIA_DIR", must_succeed=False)
        if multimedia_dir is not None:
            dependency_dispatcher.set_folder_icon(multimedia_dir, "multimedia")
            dependency_dispatcher.set_folder_icon(multimedia_dir / "avatars", "avatars")
            dependency_dispatcher.set_folder_icon(multimedia_dir / "freestyle_football", "football", True)
            dependency_dispatcher.set_folder_icon(multimedia_dir / "holidays", "holidays", True)
            dependency_dispatcher.set_folder_icon(multimedia_dir / "presentations", "presentations", True)
            dependency_dispatcher.set_folder_icon(multimedia_dir / "skydive", "skydive")
            dependency_dispatcher.set_folder_icon(multimedia_dir / "receipts", "receipts", True)
            dependency_dispatcher.set_folder_icon(multimedia_dir / "encrypted", "encrypted")
            dependency_dispatcher.set_folder_icon(multimedia_dir / "climbing", "climbing", True)
            dependency_dispatcher.set_folder_icon(multimedia_dir / "fret_saw", "fretsaw")
            dependency_dispatcher.set_folder_icon(multimedia_dir / "funny", "funny", True)
            dependency_dispatcher.set_folder_icon(multimedia_dir / "microscope", "microscope")
            dependency_dispatcher.set_folder_icon(multimedia_dir / "movies", "movies")
            dependency_dispatcher.set_folder_icon(multimedia_dir / "music", "music")
            dependency_dispatcher.set_folder_icon(multimedia_dir / "music_to_rate", "music")
            dependency_dispatcher.set_folder_icon(multimedia_dir / "tv_series", "tv_series")
            dependency_dispatcher.set_folder_icon(multimedia_dir / "wallpapers", "wallpapers")

            dependency_dispatcher.add_multimedia_directories(
                [
                    (multimedia_dir / "wallpapers", "Wallpapers"),
                    (multimedia_dir / "funny", "Multimedia/Funny"),
                    (multimedia_dir / "tv_series", "Multimedia/TvSeries"),
                    (multimedia_dir / "movies", "Multimedia/Movies"),
                ]
            )

    def _get_xdg_dir(self, name, must_succeed=True):
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

    @push_dependency_handler
    def register_homedir_file(self, file, allow_multipart=False):
        filename = Path(file)
        if filename.is_absolute():
            try:
                filename = filename.relative_to(self._paths.home())
            except ValueError:
                self._logger.log(f"ERROR: incorrect path passed: {file}")
                raise

        if len(filename.parts) != 1:
            if allow_multipart:
                filename = filename.parts[0]
            else:
                self._logger.log(f"ERROR: incorrect path passed: {file}")
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
            (self._paths.home() / xdg_dir).mkdir(exist_ok=True)

        multimedia_dir = self._get_xdg_dir("XDG_MULTIMEDIA_DIR", must_succeed=False)
        if multimedia_dir is not None:
            # These directories are excluded from sync and we'll create them manually
            (multimedia_dir / "movies").mkdir(exist_ok=True)
            (multimedia_dir / "music").mkdir(exist_ok=True)
            (multimedia_dir / "music_to_rate").mkdir(exist_ok=True)
            (multimedia_dir / "tv_series").mkdir(exist_ok=True)

    def _cleanup_existing_xdg_dirs(self):
        with self._logger.indent("Making sure existing XDG dirs are ok"):
            # We renamed some default XDG dirs to different names, so we check if they are renamed in the filesystem
            for old, new in self._xdg_renamed.values():
                old_path = self._paths.home() / old
                new_path = self._paths.home() / new

                if new_path.exists():
                    if old_path.exists():
                        try:
                            old_path.rmdir()
                            self._logger.log(f"{new_path}: OK ({old_path} existed, but it was removed)")
                        except OSError:
                            self._logger.push_warning(f"{new_path}: both {new_path} and {old_path} exist")
                    else:
                        self._logger.log(f"{new_path}: OK")
                else:
                    if old_path.exists():
                        old_path.rename(new_path)
                        self._logger.log(f"{new_path}: OK (renamed from {old_path})")
                    else:
                        new_path.mkdir()
                        self._logger.log(f"{new_path}: OK (created)")

            # We removed some default XDG dirs, so we check if they are truly gone
            for name in self._xdg_removed.values():
                path = self._paths.home() / name
                if path.exists():
                    try:
                        path.rmdir()
                        self._logger.log(f"{path}: OK (removed)")
                    except OSError:
                        self._logger.push_warning(f"{path}: directory exists, but should be removed")
                else:
                    self._logger.log(f"{path}: OK")

            # Perform above removals on startup
            removals = [f"rmdir ~/{default_value} 2>/dev/null" for default_value in self._xdg_removed.values()]
            removals += [f"rmdir ~/{default_value} 2>/dev/null" for (default_value, _) in self._xdg_renamed.values()]
            self._file_writer.write_section(
                ".config/PaiSetup/xinitrc_base",
                "Remove unused directories in HOME",
                removals,
            )

    def _setup_xdg_paths(self):
        # Prepare our custom XDG dirs specification and generate an XDG config file.
        # Note this file is not automatically sourced by the system. Some programs
        # may do it, but in general we have to do it manually in init scripts.
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

        # Prevent resetting user-dirs.dirs file on startup.
        self._file_writer.write_lines(".config/user-dirs.conf", ["enabled=false"], file_type=FileType.ConfigFile)

    def _generate_files_whitelist(self):
        """
        We generate a file containing list of files that are allowed to be in home directory.
        If there are some other files, there will be an error reported by a periodic check.
        """

        # Add PaiSetup itself
        self.register_homedir_file(self._paths.get(KnownPath.PaiSetup))

        # Add folders managed by this step
        for homedir_file in itertools.chain(
            self._xdg_defaults.values(),
            self._xdg_custom.values(),
            (x[1] for x in self._xdg_renamed.values()),
        ):
            self.register_homedir_file(homedir_file, allow_multipart=True)

        # Add loose folders not managed by any step
        self.register_homedir_file(".gnupg")

        # Generate a file with all whitelisted files (including those registered by other steps)
        self._logger.log("Generating homedir whitelist file")
        self._homedir_whitelisted_files = sorted(set(self._homedir_whitelisted_files))
        self._file_writer.write_lines(
            self._homedir_whitelist,
            self._homedir_whitelisted_files,
            file_type=FileType.ConfigFileNoComments,
            skip_recreate=True,  # If our periodic checks look at this file while it's being recreate we might get a warning
        )
