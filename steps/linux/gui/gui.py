from pathlib import Path

import utils.external_project as ext
from steps.step import Step
from utils.command import *
from utils.keybinding import KeyBinding
from utils.services.file_writer import FileType, LinePlacement

perform_called = False
push_dependencies_called = False


class GuiStep(Step):
    def perform(self):
        global perform_called
        if perform_called:
            return
        perform_called = True

        self._compile_color_generator()

        self._setup_xinitrc_base()
        self._setup_xresources_theme()
        self._file_writer.remove_file(".cache/PaiSetup/wallpapers/directories")

    def push_dependencies(self, dependency_dispatcher):
        # GuiStep is a base class for multiple steps like DwmStep or AwesomeStep. It has its
        # dependencies, but they should be pushed only once. Otherwise we'll get duplicated
        # periodic checks and keybindings. This is kind of a caveman solution to this problem,
        # but I'm not sure how else to fix it at the moment.
        if not dependency_dispatcher.is_fake:
            global push_dependencies_called
            if push_dependencies_called:
                return
            push_dependencies_called = True

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
            "udiskie",
            "flameshot",
            "pacman-contrib",  # for checkupdates
            "libnotify",
            "bc",  # for float calculations in set_brightness.sh
            "xdotool",  # for getting Thunar's cwd
        )

        dependency_dispatcher.register_periodic_daemon_check("flameshot", "flameshot")
        dependency_dispatcher.register_periodic_daemon_check("picom", "picom")
        dependency_dispatcher.register_periodic_daemon_check("[a-zA-Z/]+python[23]? [a-zA-Z/_]+udiskie", "udiskie")

        # fmt: off
        dependency_dispatcher.add_keybindings(
            KeyBinding("s").mod().shift().desc("Screenshot").execute("flameshot gui"),
            KeyBinding("b").mod().shift().desc("Browser").executeShell("$BROWSER"),
            KeyBinding("b").mod().shift().ctrl().desc("Browser (incognito)").executeShell("$BROWSER_PRIVATE"),
            KeyBinding("e").mod().desc("Files").executeShell("$FILE_MANAGER"),
            KeyBinding("w").mod().shift().desc("Change wallpaper").executeShell("$PAI_SETUP_ROOT/steps/linux/gui/scripts/select_wallpaper.py --restart_wm"),
            KeyBinding("q").mod().shift().desc("Restart GUI").executeShell("$PAI_SETUP_ROOT/steps/linux/gui/scripts/restart_wm.sh"),
            KeyBinding(["Return", "KP_Enter"]).mod().shift().desc("Terminal").executeShell("$TERMINAL"),
            KeyBinding("XF86AudioMute").executeShell("$PAI_SETUP_ROOT/steps/linux/gui/scripts/set_volume.sh 0"),
            KeyBinding("XF86AudioLowerVolume").executeShell("$PAI_SETUP_ROOT/steps/linux/gui/scripts/set_volume.sh 1"),
            KeyBinding("XF86AudioRaiseVolume").executeShell("$PAI_SETUP_ROOT/steps/linux/gui/scripts/set_volume.sh 2"),
            KeyBinding("XF86AudioLowerVolume").mod().executeShell("$PAI_SETUP_ROOT/steps/linux/gui/scripts/access_rhythmbox.sh 3 1"),
            KeyBinding("XF86AudioRaiseVolume").mod().executeShell("$PAI_SETUP_ROOT/steps/linux/gui/scripts/access_rhythmbox.sh 2 1"),
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
            [
                "rm ~/.config/PaiSetup/wallpaper",
                'PYTHONPATH="$PAI_SETUP_ROOT" $PAI_SETUP_ROOT/steps/linux/gui/scripts/select_wallpaper.py & >/dev/null',
                "until [ -f ~/.config/PaiSetup/wallpaper ]; do",
                "    sleep 0.1",
                "done",
            ],
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
