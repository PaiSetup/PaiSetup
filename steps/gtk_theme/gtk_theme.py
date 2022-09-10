from steps.step import Step
from utils import command
from utils.log import log, LogIndent
from pathlib import Path
from utils.file_writer import FileType
import os
import shutil


class GtkThemeStep(Step):
    def __init__(self, *, regenerate_emblems):
        super().__init__("GtkTheme")
        self.widget_theme_name = "Layan-dark"
        self.icon_theme_name = "LinuxSetupTheme"
        self.regenerate_emblems = regenerate_emblems

    def express_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_packages(
            "layan-gtk-theme-git",
            "gvfs",
            "sensual-breeze-icons-git",
            "lxappearance",  # not stricly needed, but useful when checking gtk themes
        )

    def perform(self):
        # TODO break this up into smaller methods

        current_step_dir = Path(__file__).parent

        log("Generating gtk 2.0 theme")  # Example application using gtk 2.0 - lxappearance
        self._file_writer.write_lines(
            ".gtkrc-2.0",
            [
                f'gtk-theme-name="{self.widget_theme_name}"',
                f'gtk-icon-theme-name="{self.icon_theme_name}"',
            ],
            file_type=FileType.ConfigFile,
        )

        log("Generating gtk 3.0 theme")  # Example application using gtk 3.0 - Thunar
        self._file_writer.write_lines(
            ".config/gtk-3.0/settings.ini",
            [
                "[Settings]",
                f"gtk-theme-name={self.widget_theme_name}",
                f"gtk-icon-theme-name={self.icon_theme_name}",
            ],
            file_type=FileType.ConfigFile,
        )

        icon_theme_directory = self._env.home() / ".local/share/icons" / self.icon_theme_name
        log(f"Creating icon theme config file in {icon_theme_directory}")
        self._file_writer.write_lines(
            icon_theme_directory / "index.theme",
            [
                "[Icon Theme]",
                f"Name={self.icon_theme_name}",
                "Comment=My custom icon theme",
                "Inherits=Sensual-Breeze-Light",
                "Example=folder",
                "Directories=emblems_64,emblems_512,",
                "",
                "[emblems_64]",
                "Context=Emblems",
                "Size=64",
                "Type=Fixed",
                "",
                "[emblems_512]",
                "Context=Emblems",
                "Size=512",
                "Type=Fixed",
            ],
            file_type=FileType.ConfigFile,
        )

        sizes_to_generate = [64]
        self.generate_downsized_emblems(sizes_to_generate)

        log("Linking emblems directories")
        command.run_command(f"ln -sfT {current_step_dir / 'emblems_64'} {icon_theme_directory / 'emblems_64'}")
        command.run_command(f"ln -sfT {current_step_dir / 'emblems_512'} {icon_theme_directory / 'emblems_512'}")

        log("Refreshing icon cache")
        command.run_command("gtk-update-icon-cache")

        log("Setting emblems to directories")
        emblems_map = {
            self._env.home() / "Desktop": ("desktop", False),
            self._env.home() / "Downloads": ("downloads", False),
            self._env.home() / "LinuxSetup": ("linux_setup", False),
            self._env.home() / "Multimedia": ("multimedia", False),
            self._env.home() / "Multimedia/Avatars": ("avatars", False),
            self._env.home() / "Multimedia/FreestyleFootball": ("football", False),
            self._env.home() / "Multimedia/FretSaw": ("fretsaw", False),
            self._env.home() / "Multimedia/Funny": ("funny", False),
            self._env.home() / "Multimedia/Icons": ("icons", False),
            self._env.home() / "Multimedia/Microscope": ("microscope", False),
            self._env.home() / "Multimedia/Movies": ("movies", False),
            self._env.home() / "Multimedia/Music": ("music", True),
            self._env.home() / "Multimedia/MusicToRate": ("music", True),
            self._env.home() / "Multimedia/TvSeries": ("tv_series", True),
            self._env.home() / "Multimedia/Wallpapers": ("wallpapers", False),
            self._env.home() / "Scripts": ("scripts", False),
            self._env.home() / "work": ("work", False),
        }
        with LogIndent():
            for path, (emblem, create_if_necessary) in emblems_map.items():
                log_line = f"{path}: {emblem}"
                if not os.path.isdir(path):
                    if create_if_necessary:
                        Path(path).mkdir(parents=True)
                    else:
                        log(f"{log_line} (warning: directory does not exists - skipping)")
                        continue
                log(log_line)
                command.run_command(f'gio set -t stringv {path} metadata::emblems "{emblem}"')

    def generate_downsized_emblems(self, sizes_to_generate):
        original_size = 512
        original_emblems_dir = current_step_dir = Path(__file__).parent / "emblems_512"

        for size_to_generate in sizes_to_generate:
            scaling_factor = size_to_generate / original_size
            downsized_emblems_dir = current_step_dir = Path(__file__).parent / f"emblems_{size_to_generate}"

            # Skip if any problems encountered or files are already generated
            if scaling_factor >= 1:
                log(f"WARNING could not generate emblems for size {size_to_generate} (bigger than original)")
                continue
            if scaling_factor * original_size != size_to_generate:
                log(f"WARNING could not generate emblems for size {size_to_generate} (division not even)")
                continue
            if downsized_emblems_dir.exists():
                if self.regenerate_emblems:
                    shutil.rmtree(downsized_emblems_dir)
                else:
                    return

            # Perform downsizing
            log(f"Generating {size_to_generate}x{size_to_generate} emblems")
            downsized_emblems_dir.mkdir()
            for original_file_path in original_emblems_dir.glob("*"):
                downsized_file_path = downsized_emblems_dir / original_file_path.name
                command.run_command(f"convert -resize {scaling_factor*100}% {original_file_path} {downsized_file_path}")
