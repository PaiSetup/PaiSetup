import os
import shutil
from pathlib import Path

from steps.step import Step
from utils import external_project as ext
from utils.command import *
from utils.dependency_dispatcher import push_dependency_handler
from utils.services.file_writer import FileType, FileWriter


class GtkThemeStep(Step):
    """
    GTK theming is a quite complicated task. Here it consists of four things:
        1. Widget theme, which defines the colors and sizes of interface elements. We generate it using a third party software
           called oomox. Colors are generated based on theme colors stored in xresources. Theme is generated in a separate bash
           script, because we want to call it after wallpapers (and the theme colors) change.
        2. Icon theme, which defines icons used for various reasons, e.g. folder icons in Thunar or custom app icons in
           ulauncher. It is based on catpuccin icon theme. Some icons were removed to make it lighter. Icons in this theme are
           defined in svg format (which is xml). We can colorize the icons, so they match the widget theme by doing find&replace
           with sed. It is done in a separate bash script (for the same reason as in 1.). Links to the icon theme:
            - https://www.gnome-look.org/p/1715570
            - https://github.com/Fausto-Korpsvart/Catppuccin-GTK-Theme
        3. Downsizing emblems. GVfs allows defining emblems for files in the filesystem. Emblems are images that will usually be
           displayed on top of a normal folder icon by GUI file managers. We have our own set of custom emblems stored as images
           of size 512x512. We also downscale them to smaller sizes, so file managers can use them and consume less memory when
           full size is not needed.
        4. GTK config, which points to location of widget theme and icon theme. There are separate configs for different versions
           of GTK. We have to generate all of them. There's no need to regenerate them after wallpaper change.
    """

    def __init__(self, *, root_build_dir, regenerate_widget_theme, regenerate_icon_theme):
        super().__init__("GtkTheme")
        self._current_step_dir = Path(__file__).parent

        # Widget theme
        self._widget_theme_name = "PaiSetupWidgetTheme"
        self._regenerate_widget_theme = regenerate_widget_theme
        self._dst_widget_theme_path = self._env.home() / ".local/share/themes" / self._widget_theme_name

        # Icon theme
        self._icon_theme_name = "PaiSetupIconTheme"
        self._regenerate_icon_theme = regenerate_icon_theme
        self._src_icon_theme_path = root_build_dir / "gtk_icon_theme"
        self._dst_icon_theme_path = self._env.home() / ".local/share/icons" / self._icon_theme_name

        self._emblems_path = root_build_dir / "gtk_emblems"
        self._emblems = {}

    def push_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_packages(
            "gvfs",
            "lxappearance",  # not stricly needed, but useful when checking gtk themes
            "themix-theme-oomox-git",
            "imagemagick",
        )

    @push_dependency_handler
    def set_folder_icon(self, path, icon_name):
        path = Path(path)
        if path in self._emblems:
            raise ValueError(f"There already exists an icon for {path}")
        self._emblems[path] = icon_name

    def perform(self):
        self._generate_emblems([64])
        self._generate_widget_theme()
        self._generate_icon_theme()
        self._assign_emblems()
        self._generate_gtk2_config()
        self._generate_gtk3_config()

    def _generate_emblems(self, sizes_to_generate):
        if not self._emblems_path.exists() or self._regenerate_icon_theme:
            self._logger.log(f"Downloading emblems ({self._emblems_path})")
            ext.download_github_zip("PaiSetup", "LinuxEmblems", self._emblems_path, re_download=True)

        src_size = 512
        src_dir = self._emblems_path / "512"

        for dst_size in sizes_to_generate:
            scaling_factor = dst_size / src_size
            dst_dir = self._emblems_path / f"{dst_size}"

            # Skip if any problems encountered or files are already generated
            if scaling_factor >= 1:
                self._logger.push_warning(f"could not generate emblems for size {dst_size} (bigger than original)")
                continue
            if scaling_factor * src_size != dst_size:
                self._logger.push_warning(f"could not generate emblems for size {dst_size} (division not even)")
                continue
            if dst_dir.exists() and self._regenerate_icon_theme:
                shutil.rmtree(dst_dir)

            # Perform downsizing if needed
            if not dst_dir.exists():
                self._logger.log(f"Generating {dst_size}x{dst_size} emblems")
                dst_dir.mkdir()
                for src_file_path in src_dir.glob("*"):
                    dst_file_path = dst_dir / src_file_path.name
                    run_command(f"convert -resize {scaling_factor*100}% {src_file_path} {dst_file_path}")

    def _generate_widget_theme(self):
        if self._dst_widget_theme_path.exists() and not self._regenerate_widget_theme:
            self._logger.log(f"Widget theme already generated")
            return

        self._logger.log(f"Generating widget theme ({self._dst_widget_theme_path})")
        command = str(self._current_step_dir / "generate_widget_theme.sh")
        run_command(command, shell=True)

    def _generate_icon_theme(self):
        if self._dst_icon_theme_path.exists() and not self._regenerate_icon_theme:
            self._logger.log(f"Icon theme already generated")
            return

        self._logger.log(f"Downloading icon theme ({self._src_icon_theme_path})")
        ext.download_github_zip("PaiSetup", "GtkIconTheme", self._src_icon_theme_path, re_download=self._regenerate_icon_theme)

        self._logger.log(f"Generating icon theme ({self._dst_icon_theme_path})")
        command = str(self._current_step_dir / "generate_icon_theme.sh")
        run_command(command, shell=True)

    def _assign_emblems(self):
        self._logger.log("Setting emblems to directories")
        with self._logger.indent():
            for path, emblem in self._emblems.items():
                resolved_path = self._file_writer.resolve_path(path)
                log_line = f"{resolved_path}: {emblem}"
                if not os.path.isdir(resolved_path):
                    self._logger.log(f"{log_line} (warning: directory does not exist - skipping)")
                    continue
                self._logger.log(log_line, short_message=emblem)
                run_command(f'gio set -t stringv {resolved_path} metadata::emblems "{emblem}"')

    def _generate_gtk2_config(self):
        self._logger.log("Generating gtk 2.0 config")  # Example application using gtk 2.0 - lxappearance
        self._file_writer.write_section(
            ".config/PaiSetup/xinitrc_base",
            "Ensure gkt2 configs are in ~/.config",
            ['export GTK2_RC_FILES="$HOME/.config/gtk-2.0/gtkrc"'],
        )
        self._file_writer.write_lines(
            ".config/gtk-2.0/gtkrc",
            [
                f'gtk-theme-name="{self._widget_theme_name}"',
                f'gtk-icon-theme-name="{self._icon_theme_name}"',
            ],
            file_type=FileType.ConfigFile,
        )

    def _generate_gtk3_config(self):
        self._logger.log("Generating gtk 3.0 config")  # Example application using gtk 3.0 - Thunar
        self._file_writer.write_lines(
            ".config/gtk-3.0/settings.ini",
            [
                "[Settings]",
                f"gtk-theme-name={self._widget_theme_name}",
                f"gtk-icon-theme-name={self._icon_theme_name}",
            ],
            file_type=FileType.ConfigFile,
        )
