from steps.step import Step
from utils import command
from steps.dotfiles import FileType
from pathlib import Path
import utils.external_project as ext
import json


class GuiStep(Step):
    def _perform_impl(self):
        colors_dir = self.root_build_dir / "colors"
        ext.download(
            "git://git.2f30.org/colors",
            "8edb1839c1d2a62fbd1d4447f802997896c2b0c0",
            colors_dir,
            fetch=self.fetch_git,
            clean=False,
        )
        ext.make(colors_dir)

    def express_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_packages(
            "xorg-xrandr",
            "xorg-xinit",
            "xorg-server",
            "nitrogen",
            "picom-ibhagwan-git",
            "ulauncher",
            "libxft-bgra",
            "xorg-setxkbmap",
            "yad",
            "flameshot",
            "pacman-contrib",  # for checkupdates
            "libnotify",
            "bc",  # for float calculations in set_brightness.sh
        )
        dependency_dispatcher.add_assumed_packages(
            [
                "libxft=2.3.3",  # Some packages have this as a dependency, but we actually need libxft-bgra
            ]
        )
        self._setup_xinitrc_base(dependency_dispatcher)
        self._setup_xresources_theme(dependency_dispatcher)
        self._setup_ulauncher_config(dependency_dispatcher)

    def _setup_xresources_theme(self, dependency_dispatcher):
        dependency_dispatcher.add_dotfile_lines(
            ".config/Xresources.theme",
            ["#define COL_THEME1 #008866"],
            file_type=FileType.XResources,
        )

    def _setup_xinitrc_base(self, dependency_dispatcher):
        dependency_dispatcher.add_dotfile_section(
            ".config/LinuxSetup/xinitrc_base",
            "Basic graphical settings",
            [
                "(sleep 0.1 ; xrandr --output Virtual-1 --mode 1920x1080) &",
                "$LINUX_SETUP_ROOT/steps/gui/set_random_wallpaper.sh 1 &",
            ],
        )
        dependency_dispatcher.add_dotfile_section(
            ".config/LinuxSetup/xinitrc_base",
            "Button names for statusbar scripts",
            [
                "export BUTTON_ACTION=1",
                "export BUTTON_TERMINATE=2",
                "export BUTTON_INFO=3",
                "export BUTTON_SCROLL_UP=4",
                "export BUTTON_SCROLL_DOWN=5",
            ],
        )
        dependency_dispatcher.add_dotfile_section(
            ".config/LinuxSetup/xinitrc_base",
            "Load Xresources",
            ["xrdb ~/.config/Xresources"],
        )
        dependency_dispatcher.add_dotfile_section(
            ".config/LinuxSetup/xinitrc_base",
            "Polish keyboard layout",
            ["(sleep 1; setxkbmap pl) &"],
        )
        dependency_dispatcher.add_dotfile_section(
            ".config/LinuxSetup/xinitrc_base",
            "Screenshot daemon",
            ["flameshot &"],
        )
        dependency_dispatcher.add_dotfile_section(
            ".config/LinuxSetup/xinitrc_base",
            "App launcher",
            ["ulauncher --hide-window &"],
        )
        dependency_dispatcher.add_dotfile_section(
            ".config/LinuxSetup/xinitrc_base",
            "Run browser",
            ["$BROWSER &"],
        )

    def _setup_ulauncher_config(self, dependency_dispatcher):
        config = {
            "blacklisted-desktop-dirs": "/usr/share/locale:/usr/share/app-install:/usr/share/kservices5:/usr/share/fk5:/usr/share/kservicetypes5:/usr/share/applications/screensavers:/usr/share/kde4:/usr/share/mimelnk",
            "clear-previous-query": True,
            "disable-desktop-filters": False,
            "grab-mouse-pointer": True,
            "hotkey-show-app": "<Super>grave",
            "render-on-screen": "mouse-pointer-monitor",
            "show-indicator-icon": True,
            "show-recent-apps": "3",
            "terminal-command": "",
            "theme-name": "dark",
        }
        config = json.dumps(config, indent=4)

        dependency_dispatcher.add_dotfile_lines(".config/ulauncher/settings.json", [config], file_type=FileType.Json)
