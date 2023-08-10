from steps.step import Step, dependency_listener
from pathlib import Path
import os
from utils.log import log, LogIndent
from utils import command
from utils.file_writer import FileType


class HomeDirectoryStep(Step):
    def __init__(self, is_main_machine):
        super().__init__("HomeDirectory")
        self._is_main_machine = is_main_machine

        self._multimedia_dir = self._env.home() / "multimedia"
        self._work_dir = self._env.home() / "work"

        self._homedir_whitelist = Path(__file__).parent / "homedir_whitelist"
        self._homedir_whitelisted_files = []

    def express_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.set_folder_icon("desktop", "desktop")
        dependency_dispatcher.set_folder_icon("downloads", "downloads")
        dependency_dispatcher.set_folder_icon("mounts", "mounts")
        dependency_dispatcher.set_folder_icon(self._work_dir, "work")
        dependency_dispatcher.set_folder_icon(self._env.get("PAI_SETUP_ROOT"), "pai_setup")

        check_script = Path(__file__).parent / "setup_mount_dir.sh"
        dependency_dispatcher.register_periodic_check(check_script, 3)

        check_script = Path(__file__).parent / "verify_homedir.sh"
        dependency_dispatcher.register_periodic_check(check_script, 45, multi_line=True)

        if self._is_main_machine:
            dependency_dispatcher.set_folder_icon(self._multimedia_dir, "multimedia")
            dependency_dispatcher.set_folder_icon(self._multimedia_dir / "avatars", "avatars")
            dependency_dispatcher.set_folder_icon(self._multimedia_dir / "freestyle_football", "football")
            dependency_dispatcher.set_folder_icon(self._multimedia_dir / "fret_saw", "fretsaw")
            dependency_dispatcher.set_folder_icon(self._multimedia_dir / "funny", "funny")
            dependency_dispatcher.set_folder_icon(self._multimedia_dir / "icons", "icons")
            dependency_dispatcher.set_folder_icon(self._multimedia_dir / "microscope", "microscope")
            dependency_dispatcher.set_folder_icon(self._multimedia_dir / "movies", "movies")
            dependency_dispatcher.set_folder_icon(self._multimedia_dir / "music", "music")
            dependency_dispatcher.set_folder_icon(self._multimedia_dir / "music_to_rate", "music")
            dependency_dispatcher.set_folder_icon(self._multimedia_dir / "tv_series", "tv_series")
            dependency_dispatcher.set_folder_icon(self._multimedia_dir / "wallpapers", "wallpapers")

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

    @dependency_listener
    def register_homedir_file(self, file, **kwargs):
        filename = Path(file)
        if filename.is_absolute():
            try:
                filename = filename.relative_to("/home/maciej")
            except ValueError:
                log(f"ERROR: incorrect path passed: {file}")
                raise

        if len(filename.parts) != 1:
            log(f"ERROR: incorrect path passed: {file}")
            raise ValueError()

        self._homedir_whitelisted_files.append(str(filename))

    def _create_directories(self):
        self._work_dir.mkdir(parents=True, exist_ok=True)
        (self._env.home() / ".log").mkdir(exist_ok=True)
        (self._env.home() / ".local/state").mkdir(exist_ok=True)
        (self._env.home() / ".local/share").mkdir(exist_ok=True)

        if self._is_main_machine and self._multimedia_dir.exists():
            # These directories are excluded from sync and we'll create them manually
            (self._multimedia_dir / "movies").mkdir(exist_ok=True)
            (self._multimedia_dir / "music").mkdir(exist_ok=True)
            (self._multimedia_dir / "music_to_rate").mkdir(exist_ok=True)
            (self._multimedia_dir / "tv_series").mkdir(exist_ok=True)

    def _cleanup_existing_xdg_dirs(self):
        with LogIndent("Making sure existing XDG dirs are ok"):
            # We renamed some default XDG dirs to different names, so we check if they are renamed in the filesystem
            renamed_map = [
                ("Desktop", "desktop"),
                ("Downloads", "downloads"),
            ]
            for old, new in renamed_map:
                old_path = self._env.home() / old
                new_path = self._env.home() / new

                if new_path.exists():
                    if old_path.exists():
                        try:
                            old_path.rmdir()
                            log(f"{new_path}: OK ({old_path} existed, but it was removed)")
                        except OSError:
                            log(f"{new_path}: WARNING - both {new_path} and {old_path} exist")
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
            removed_map = [
                "Templates",
                "Public",
                "Documents",
                "Music",
                "Pictures",
                "Videos",
            ]
            for name in removed_map:
                path = self._env.home() / name
                if path.exists():
                    try:
                        path.rmdir()
                        log(f"{path}: OK (removed)")
                    except OSError:
                        log(f"{path}: WARNING - {path} exists, but should be removed")
                else:
                    log(f"{path}: OK")
            self._file_writer.write_section(
                ".config/PaiSetup/xinitrc_base",
                "Remove unused directories in HOME",
                [ f"rmdir ~/{x} 2>/dev/null" for x in removed_map] + [ f"rmdir ~/{x} 2>/dev/null" for x, _ in renamed_map]
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

    def _generate_files_whitelist(self):
        """
        We generate a file containing list of files that are allowed to be in home directory.
        If there are some other files, there will be an error reported by a periodic check.
        """

        # First add folders managed by this step
        self.register_homedir_file(self._multimedia_dir)
        self.register_homedir_file(self._work_dir)
        self.register_homedir_file("desktop")
        self.register_homedir_file("downloads")
        self.register_homedir_file("mounts")
        self.register_homedir_file("vm")
        self.register_homedir_file(".profile")
        self.register_homedir_file(".log")
        self.register_homedir_file(".cache")
        self.register_homedir_file(".config")
        self.register_homedir_file(".local")
        self.register_homedir_file(self._env.get("PAI_SETUP_ROOT"))

        # Add some files which don't belong to any step and it's not worth creating new steps
        self.register_homedir_file(".ssh")

        # Generate a file with all files (including those registered by other steps)
        log("Generating homedir whitelist file")
        self._homedir_whitelisted_files = sorted(set(self._homedir_whitelisted_files))
        self._file_writer.write_lines(self._homedir_whitelist, self._homedir_whitelisted_files, file_type=FileType.ConfigFileNoComments)
