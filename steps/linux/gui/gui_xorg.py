from pathlib import Path

import utils.external_project as ext
from steps.step import Step
from utils.command import *
from utils.dependency_dispatcher import push_dependency_handler
from utils.keybinding import KeyBinding
from utils.os_function import LinuxDistro
from utils.services.file_writer import FileType


class WindowManagerXorg:
    def __init__(self, name, xsession_name, launch_command):
        self.name = name
        self.xsession_name = xsession_name
        self.launch_command = launch_command
        self.config_path = Path(os.environ["HOME"]) / f".config/PaiSetup/{name}"


class GuiXorg(Step):
    def __init__(self, full, root_build_dir):
        super().__init__("GuiXorg")
        self._full = full
        self._root_build_dir = root_build_dir
        self._window_managers = []

    def perform(self):
        self._compile_color_generator()
        self._generate_picom_config()
        self._generate_xinitrc_base()
        self._generate_xinitrc_per_wm()
        self._generate_xsession_per_wm()
        self._generate_xresources_per_wm()

        self._file_writer.remove_file(".cache/PaiSetup/wallpapers/directories")

    @push_dependency_handler
    def register_xorg_wm(self, wm):
        self._window_managers.append(wm)

    def push_dependencies(self, dependency_dispatcher):
        # TODO move all non-x11 stuff to different steps
        dependency_dispatcher.add_packages(
            "xorg-xrandr",
            "xorg-xinit",
            "xorg-server",
            "xorg-server-xephyr",
            "xorg-xwininfo",
            "xorg-xev",
            "xclip",
            "nitrogen",
            "picom",
            "libxft",
            "xorg-setxkbmap",
            "yad",
            "udiskie",
            "flameshot",
            "pacman-contrib",  # for checkupdates on arch
            "libnotify",
            "bc",  # for float calculations in set_brightness.sh
            "xdotool",  # for getting Thunar's cwd
            "cava",
        )
        if LinuxDistro.current().is_debian_like():
            dependency_dispatcher.add_packages("libpng-dev")  # needed for compiling color generator on Debian

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
            self._logger.log('Compiling "colors" binary')
            colors_dir = self._root_build_dir / "colors"
            ext.download(
                "git://git.2f30.org/colors",
                "8edb1839c1d2a62fbd1d4447f802997896c2b0c0",
                colors_dir,
                logger=self._logger,
                fetch=self._full,
                clean=False,
            )
            ext.make(colors_dir, logger=self._logger)

    def _generate_picom_config(self):
        self._logger.log("Generating picom config")
        self._file_writer.write_lines(
            ".config/picom.conf",
            [
                'backend = "xrender"',
                "vsync = true;",
                "fade-in-step = 1;",
                "fade-out-step = 1;",
                "frame-opacity = 0;",
                "corner-radius = 10;",
            ],
            skip_recreate=True,  # picom watches for config file changes and crashes when we recreate it
        )

    def _generate_xinitrc_base(self):
        self._logger.log(f"Generating xinitrc_base")
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
        self._file_writer.write_section(
            ".config/PaiSetup/xinitrc_base",
            "Run picom",
            ["picom -b &"],
        )

    def _generate_xinitrc_per_wm(self):
        for wm in self._window_managers:
            self._logger.log(f"Generating xinitrc for {wm.name}")

            self._file_writer.write_lines(
                wm.config_path / "xinitrc",
                [
                    f"export WM={wm.name}",
                    ". ~/.config/PaiSetup/xinitrc_base",
                    f"exec {wm.launch_command}",
                ],
            )

    def _generate_xsession_per_wm(self):
        for wm in self._window_managers:
            xinitrc_path = wm.config_path / "xinitrc"

            self._logger.log(f"Creating a script and .desktop file for {wm.xsession_name} session")

            # First create a script that simply calls our xinitrc. Unfortunately we cannot create
            # a reusable script and simply pass an argument in .desktop file, because some DMs
            # (namely LightDM) ignore .desktop files containing arguments to commands.
            script_name = self._file_writer.write_executable_script(
                f"xsession_run_{wm.xsession_name}",
                [
                    "export XDG_SESSION_TYPE=x11",
                    f"export XDG_SESSION_DESKTOP={wm.xsession_name}",
                    f"export XDG_CURRENT_DESKTOP={wm.name}",
                    "",
                    f'exec "{xinitrc_path}"',
                ],
            )

            # Then create a .desktop file. DMs should scan /usr/share/xsession and allow selecting
            # them in order to launch a specific session.
            self._file_writer.write_lines(
                f"/usr/share/xsessions/{wm.xsession_name}.desktop",
                [
                    "[Desktop Entry]",
                    f"Name={wm.xsession_name}",
                    f"Comment=Executes {xinitrc_path} script",
                    f"Exec={script_name}",
                    f"TryExec={script_name}",
                    "Type=Application",
                ],
                file_type=FileType.ConfigFile,
            )

    def _generate_xresources_per_wm(self):
        for wm in self._window_managers:
            self._logger.log(f"Generating Xresources for {wm.name}")

            # This value is pulled to a different file, so that we can update it easily from a script.
            # The color hardcoded here is a placeholder. It will be written by select_wallpaper.py.
            self._file_writer.write_lines(
                wm.config_path / "XresourcesTheme",
                ["#define COL_THEME1 #008866"],
                file_type=FileType.XResources,
            )

            # Main Xresources file that should be loaded using xrdb. It is done by select_wallpaper.py
            self._file_writer.write_lines(
                wm.config_path / "Xresources",
                [
                    f'#include "{wm.config_path / "XresourcesTheme"}"',
                    "#define COL_THEME2 #878787",
                    "#define COL_THEME3 #555555",
                    "",
                    "color1: COL_THEME1",
                    "color2: COL_THEME2",
                    "color3: COL_THEME3",
                    "color4: #ffffff",
                ],
                file_type=FileType.XResources,
            )
