from pathlib import Path

import utils.external_project as ext
from steps.step import Step
from utils import command
from utils.keybinding import KeyBinding
from utils.services.file_writer import FileType

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
            "xorg-server-xephyr",
            "xorg-xwininfo",
            "nitrogen",
            "picom-ibhagwan-git",
            "libxft",
            "xorg-setxkbmap",
            "yad",
            "flameshot",
            "pacman-contrib",  # for checkupdates
            "libnotify",
            "bc",  # for float calculations in set_brightness.sh
        )

        # fmt: off
        dependency_dispatcher.add_keybindings(
            KeyBinding("s").mod().shift().desc("Screenshot").execute("flameshot gui"),
            KeyBinding("b").mod().shift().desc("Browser").executeShell("$BROWSER"),
            KeyBinding("b").mod().shift().ctrl().desc("Browser (incognito)").executeShell("$BROWSER_PRIVATE"),
            KeyBinding("e").mod().shift().desc("Files").executeShell("$FILE_MANAGER"),
            KeyBinding("w").mod().shift().desc("Change wallpaper").executeShell("$PAI_SETUP_ROOT/steps/linux/gui/scripts/select_random_wallpaper.sh --restart_wm"),
            KeyBinding("q").mod().shift().desc("Restart GUI").executeShell("$PAI_SETUP_ROOT/steps/linux/gui/scripts/restart_wm.sh"),
            KeyBinding(["Return", "KP_Enter"]).mod().shift().desc("Terminal").executeShell("$TERMINAL"),
        )
        # fmt: on

        dependency_dispatcher.register_homedir_file(".Xauthority")
        dependency_dispatcher.register_homedir_file(".xsession-errors")
        dependency_dispatcher.register_homedir_file(".xsession-errors.old")

    def _compile_color_generator(self):
        if ext.should_build(self._full, ["colors"]):
            colors_dir = self.root_build_dir / "colors"
            ext.download(
                "git://git.2f30.org/colors",
                "8edb1839c1d2a62fbd1d4447f802997896c2b0c0",
                colors_dir,
                logger=self._logger,
                fetch=self._full,
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
            ["$PAI_SETUP_ROOT/steps/linux/gui/scripts/select_random_wallpaper.sh & >/dev/null"],
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

    def _setup_picom_config(self):
        self._file_writer.write_lines(
            ".config/picom.conf",
            ["vsync = true;"],
        )
