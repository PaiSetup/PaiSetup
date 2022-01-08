from steps.step import Step
from utils import command
from steps.dotfiles import FileType
from pathlib import Path
import json


class GuiStep(Step):
    def _perform_impl(self):
        self._compile_remote_project(
            self.root_build_dir / "colors",
            "git://git.2f30.org/colors",
            "8edb1839c1d2a62fbd1d4447f802997896c2b0c0",
            None,
            self.setup_repo,
        )

    def express_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_packages(
            "sxhkd",
            "xorg-xrandr",
            "xorg-xinit",
            "xorg-server",
            "nitrogen",
            "picom-ibhagwan-git",
            "dunst",
            "ulauncher",
            "xorg-setxkbmap",
            "stalonetray",
            "yad",
            "flameshot",
        )
        self._setup_xinitrc(dependency_dispatcher)
        self._setup_dunstrc(dependency_dispatcher)
        self._setup_sxhkdrc(dependency_dispatcher)
        self._setup_picom_config(dependency_dispatcher)
        self._setup_xresources_theme(dependency_dispatcher)
        self._setup_ulauncher_config(dependency_dispatcher)

    def _setup_xresources_theme(self, dependency_dispatcher):
        dependency_dispatcher.add_dotfile_lines(
            ".config/Xresources.theme",
            ["#define COL_THEME1 #008866"],
            file_type=FileType.XResources,
        )

    def _setup_xinitrc(self, dependency_dispatcher):
        dependency_dispatcher.add_dotfile_section(
            ".xinitrc",
            "Basic graphical settings",
            [
                "(sleep 0.1 ; xrandr --output Virtual-1 --mode 1920x1080) &",
                "$LINUX_SETUP_ROOT/steps/gui/set_random_wallpaper.sh 1 &",
                "picom -b --no-fading-openclose --config ~/.config/picom.conf &",
            ],
        )

        dependency_dispatcher.add_dotfile_section(
            ".xinitrc",
            "Polish keyboard layout",
            ["(sleep 1; setxkbmap pl) &"],
        )
        dependency_dispatcher.add_dotfile_section(
            ".xinitrc",
            "Notification daemon",
            ["dunst &"],
        )
        dependency_dispatcher.add_dotfile_section(
            ".xinitrc",
            "Keybindings daemon",
            ["sxhkd &"],
        )
        dependency_dispatcher.add_dotfile_section(
            ".xinitrc",
            "Screenshot daemon",
            ["flameshot &"],
        )
        dependency_dispatcher.add_dotfile_section(
            ".xinitrc",
            "App launcher",
            ["ulauncher --hide-window &"],
        )
        dependency_dispatcher.add_dotfile_section(
            ".xinitrc",
            "Run browser",
            ["$BROWSER &"],
        )

    def _setup_dunstrc(self, dependency_dispatcher):
        current_step_dir = Path(__file__).parent

        dependency_dispatcher.add_dotfile_symlink(
            src=current_step_dir / "dunstrc",
            link=".config/dunst/dunstrc",
            prepend_home_dir_src=False,
            prepend_home_dir_link=True,
        )

    def _setup_sxhkdrc(self, dependency_dispatcher):
        dependency_dispatcher.add_dotfile_lines(
            ".config/sxhkd/sxhkdrc",
            [
                "super + shift + {Return, KP_Enter}",
                "    $TERMINAL",
                "",
                "super + shift + {BackSpace, l}",
                "    $LINUX_SETUP_ROOT/steps/gui/shutdown.sh",
                "",
                "{XF86AudioMute, XF86AudioLowerVolume, XF86AudioRaiseVolume}",
                "    $LINUX_SETUP_ROOT/steps/gui/set_volume.sh {0,1,2} 1",
                "",
                "super + {XF86AudioLowerVolume, XF86AudioRaiseVolume}",
                "    $LINUX_SETUP_ROOT/steps/gui/set_brightness.sh {0,1}",
                "",
                "super + control + {XF86AudioLowerVolume, XF86AudioRaiseVolume}",
                "    $LINUX_SETUP_ROOT/steps/gui/access_rhythmbox.sh {3,2} 1",
                "",
                "super + shift + s",
                "    flameshot gui",
                "",
                "Print",
                "    flameshot screen -c",
                "",
                "super + shift + w",
                "    $LINUX_SETUP_ROOT/steps/gui/set_random_wallpaper.sh 0",
                "",
                "super + shift + b",
                "    $BROWSER",
                "",
                "super + shift + e",
                "    $FILE_MANAGER",
                "",
                "super + control + shift + x",
                "    $LINUX_SETUP_ROOT/steps/gui/veracrypt/mount_nice.sh",
                "",
                "super + control + shift + r",
                "    $LINUX_SETUP_ROOT/steps/gui/veracrypt/mount_receipts.sh",
            ],
            file_type=FileType.Sxhkd,
        )

    def _setup_picom_config(self, dependency_dispatcher):
        dependency_dispatcher.add_dotfile_lines(
            ".config/picom.conf",
            ["corner-radius = 8"],
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
