from steps.step import Step
from utils import command
from utils.services.file_writer import FileType
from pathlib import Path
import utils.external_project as ext
import json
from utils.keybinding import KeyBinding

perform_called = False
express_dependencies_called = False


class GuiStep(Step):
    def perform(self):
        global perform_called
        if perform_called:
            return
        perform_called = True

        self._compile_color_generator()

        self._setup_xinitrc_base()
        self._setup_xresources_theme()
        self._setup_ulauncher_config()
        self._file_writer.remove_file(".cache/PaiSetupWallpapers/directories")

    def express_dependencies(self, dependency_dispatcher):
        global express_dependencies_called
        if express_dependencies_called:
            return
        express_dependencies_called = True

        dependency_dispatcher.add_packages(
            "xorg-xrandr",
            "xorg-xinit",
            "xorg-server",
            "nitrogen",
            "picom-ibhagwan-git",
            "ulauncher",
            "libxft",
            "xorg-setxkbmap",
            "yad",
            "flameshot",
            "pacman-contrib",  # for checkupdates
            "libnotify",
            "bc",  # for float calculations in set_brightness.sh
        )

        dependency_dispatcher.add_keybindings(
            KeyBinding("s").mod().shift().execute("flameshot gui"),
            KeyBinding("b").mod().shift().executeShell("$BROWSER"),
            KeyBinding("b").mod().shift().ctrl().executeShell("$BROWSER_PRIVATE"),
            KeyBinding("e").mod().shift().executeShell("$FILE_MANAGER"),
        )

        dependency_dispatcher.register_homedir_file(".Xauthority")
        dependency_dispatcher.register_homedir_file(".xsession-errors")
        dependency_dispatcher.register_homedir_file(".xsession-errors.old")

    def _compile_color_generator(self):
        colors_dir = self.root_build_dir / "colors"
        ext.download(
            "git://git.2f30.org/colors",
            "8edb1839c1d2a62fbd1d4447f802997896c2b0c0",
            colors_dir,
            logger=self._logger,
            fetch=self.fetch_git,
            clean=False,
        )
        ext.make(colors_dir, logger=self._logger)

    def _setup_xresources_theme(self):
        self._file_writer.write_lines(
            ".config/XresourcesTheme",
            ["#define COL_THEME1 #008866"],
            file_type=FileType.XResources,
        )

    def _setup_xinitrc_base(
        self,
    ):
        self._file_writer.write_section(
            ".config/PaiSetup/xinitrc_base",
            "Start in home directory",
            ["cd || exit"],
        )
        self._file_writer.write_section(
            ".config/PaiSetup/xinitrc_base",
            "Automounting daemon",
            ["udiskie &"],
        )
        self._file_writer.write_section(
            ".config/PaiSetup/xinitrc_base",
            "Source xinitrc.d scripts",
            [
                "if [ -d /etc/X11/xinit/xinitrc.d ] ; then",
                "   for f in /etc/X11/xinit/xinitrc.d/?*.sh ; do",
                '       [ -x "$f" ] && . "$f"',
                "       done",
                "    unset f",
                "fi",
            ],
        )
        self._file_writer.write_section(
            ".config/PaiSetup/xinitrc_base",
            "Set wallpaper",
            ["$PAI_SETUP_ROOT/steps/linux/gui/select_random_wallpaper.sh 0"],
        )
        self._file_writer.write_section(
            ".config/PaiSetup/xinitrc_base",
            "Button names for statusbar scripts",
            [
                "export BUTTON_ACTION=1",
                "export BUTTON_TERMINATE=2",
                "export BUTTON_INFO=3",
                "export BUTTON_SCROLL_UP=4",
                "export BUTTON_SCROLL_DOWN=5",
            ],
        )
        self._file_writer.write_section(
            ".config/PaiSetup/xinitrc_base",
            "Override locations of X11 logs",
            ['export ERRFILE="$XDG_CACHE_HOME/X11/xsession-errors"'],
        )
        self._file_writer.write_section(
            ".config/PaiSetup/xinitrc_base",
            "Polish keyboard layout",
            ["(sleep 1; setxkbmap pl) &"],
        )
        self._file_writer.write_section(
            ".config/PaiSetup/xinitrc_base",
            "Set screen save timeout duration to 2 hours",
            ["xset s 7200 &"],
        )
        self._file_writer.write_section(
            ".config/PaiSetup/xinitrc_base",
            "Screenshot daemon",
            ["flameshot &"],
        )
        self._file_writer.write_section(
            ".config/PaiSetup/xinitrc_base",
            "App launcher",
            ["ulauncher --hide-window &"],
        )

    def _setup_ulauncher_config(self):
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

        self._file_writer.write_lines(".config/ulauncher/settings.json", [config], file_type=FileType.Json)

    def _setup_picom_config(self):
        self._file_writer.write_lines(
            ".config/picom.conf",
            ["vsync = true;"],
        )
