from steps.step import Step
import os
from utils.log import log, LogIndent
from utils import command


class HomeDirectoryStep(Step):
    def __init__(self, is_main_machine):
        super().__init__("HomeDirectory")
        self._is_main_machine = is_main_machine

        self._work_dir = self._env.home() / "work"

    def express_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_packages("xdg-user-dirs")

        dependency_dispatcher.set_folder_icon("desktop", "desktop")
        dependency_dispatcher.set_folder_icon("downloads", "downloads")
        dependency_dispatcher.set_folder_icon(self._work_dir, "work")
        dependency_dispatcher.set_folder_icon(self._env.get("LINUX_SETUP_ROOT"), "linux_setup")

        if self._is_main_machine:
            multimedia_dir = self._env.home() / "multimedia"
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

    def perform(self):
        self._work_dir.mkdir(parents=True, exist_ok=True)
        self._cleanup_existing_xdg_dirs()
        self._setup_xdg_paths()

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

    def _setup_xdg_paths(self):
        self._file_writer.write_lines(
            ".config/user-dirs.dirs",
            [
                # Renamed dirs
                'XDG_DESKTOP_DIR="$HOME/desktop"',
                'XDG_DOWNLOAD_DIR="$HOME/downloads"',
                # Removed dirs
                # From https://www.freedesktop.org/wiki/Software/xdg-user-dirs/:
                # "To disable a directory, point it to the homedir. If you delete it it will be recreated on the next login."
                'XDG_TEMPLATES_DIR="$HOME"',
                'XDG_PUBLICSHARE_DIR="$HOME"',
                'XDG_DOCUMENTS_DIR="$HOME"',
                'XDG_MUSIC_DIR="$HOME"',
                'XDG_PICTURES_DIR="$HOME"',
                'XDG_VIDEOS_DIR="$HOME"',
            ],
        )
        command.run_command("xdg-user-dirs-update")
