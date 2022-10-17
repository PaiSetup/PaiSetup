from steps.step import Step
from utils import command
from utils.log import log, LogIndent
from pathlib import Path
from utils.file_writer import FileType, FileWriter
import os
import shutil


class GtkThemeStep(Step):
    def __init__(self, *, regenerate_widget_theme, regenerate_icon_theme):
        super().__init__("GtkTheme")
        self.widget_theme_name = "LinuxSetupWidgetTheme"
        self.icon_theme_name = "LinuxSetupIconTheme"
        self._regenerate_widget_theme = regenerate_widget_theme
        self._regenerate_icon_theme = regenerate_icon_theme
        self._widget_theme_path = self._env.home() / ".themes" / self.widget_theme_name  # TODO can it be moved to ~/.local?
        self._icon_theme_path = self._env.home() / ".local/share/icons" / self.icon_theme_name
        self._current_step_dir = Path(__file__).parent
        self._emblems = {}

    def express_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_packages(
            "gvfs",
            "lxappearance",  # not stricly needed, but useful when checking gtk themes
        )

    def set_folder_icon(self, path, icon_name, **kwargs):
        path = Path(path)
        if path in self._emblems:
            raise ValueError(f"There already exists an icon for {path}")
        self._emblems[path] = icon_name

    def register_as_dependency_listener(self, dependency_dispatcher):
        dependency_dispatcher.register_listener(self.set_folder_icon)

    def perform(self):
        self._generate_widget_theme()
        self._generate_icon_theme()
        self._generate_downsized_emblems([64])
        self._assign_emblems()
        self._generate_gtk2_config()
        self._generate_gtk3_config()

    def _generate_widget_theme(self):
        if self._widget_theme_path.exists() and not self._regenerate_widget_theme:
            log(f"Widget theme {self._widget_theme_path} already present")
            return
        log(f"Widget theme {self._widget_theme_path} generation")
        command.run_command(str(self._current_step_dir / "generate_widget_theme.sh"), shell=True)

    def _generate_icon_theme(self):
        if self._icon_theme_path.exists() and not self._regenerate_icon_theme:
            log(f"Icon theme {self._icon_theme_path} already present")
            return
        log(f"Icon theme {self._icon_theme_path} generation")
        command.run_command(str(self._current_step_dir / "generate_icon_theme.sh"), shell=True)

    def _generate_downsized_emblems(self, sizes_to_generate):
        original_size = 512
        original_emblems_dir = Path(__file__).parent / "emblems_512"

        for size_to_generate in sizes_to_generate:
            scaling_factor = size_to_generate / original_size
            downsized_emblems_dir = Path(__file__).parent / f"emblems_{size_to_generate}"

            # Skip if any problems encountered or files are already generated
            if scaling_factor >= 1:
                log(f"WARNING could not generate emblems for size {size_to_generate} (bigger than original)")
                continue
            if scaling_factor * original_size != size_to_generate:
                log(f"WARNING could not generate emblems for size {size_to_generate} (division not even)")
                continue
            if downsized_emblems_dir.exists():
                if self._regenerate_icon_theme:
                    shutil.rmtree(downsized_emblems_dir)
                else:
                    return

            # Perform downsizing
            log(f"Generating {size_to_generate}x{size_to_generate} emblems")
            downsized_emblems_dir.mkdir()
            for original_file_path in original_emblems_dir.glob("*"):
                downsized_file_path = downsized_emblems_dir / original_file_path.name
                command.run_command(f"convert -resize {scaling_factor*100}% {original_file_path} {downsized_file_path}")

    def _assign_emblems(self):
        log("Setting emblems to directories")
        with LogIndent():
            for path, emblem in self._emblems.items():
                resolved_path = FileWriter.resolve_path(path)
                log_line = f"{resolved_path}: {emblem}"
                if not os.path.isdir(resolved_path):
                    log(f"{log_line} (warning: directory does not exist - skipping)")
                    continue
                log(log_line)
                command.run_command(f'gio set -t stringv {resolved_path} metadata::emblems "{emblem}"')

    def _generate_gtk2_config(self):
        log("Generating gtk 2.0 config")  # Example application using gtk 2.0 - lxappearance
        self._file_writer.write_lines(".config/LinuxSetup/xinitrc_base", ['export GTK2_RC_FILES="$HOME/.config/gtk-2.0/gtkrc"'])
        self._file_writer.write_lines(
            ".config/gtk-2.0/gtkrc",
            [
                f'gtk-theme-name="{self.widget_theme_name}"',
                f'gtk-icon-theme-name="{self.icon_theme_name}"',
            ],
            file_type=FileType.ConfigFile,
        )

    def _generate_gtk3_config(self):
        log("Generating gtk 3.0 config")  # Example application using gtk 3.0 - Thunar
        self._file_writer.write_lines(
            ".config/gtk-3.0/settings.ini",
            [
                "[Settings]",
                f"gtk-theme-name={self.widget_theme_name}",
                f"gtk-icon-theme-name={self.icon_theme_name}",
            ],
            file_type=FileType.ConfigFile,
        )
