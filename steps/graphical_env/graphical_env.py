from steps.step import Step
from utils import command
from steps.dotfiles import FileType
from pathlib import Path


class GraphicalEnvStep(Step):
    def _perform_impl(self):
        self._compile_remote_project(
            self.root_build_dir / "colors",
            "git://git.2f30.org/colors",
            "8edb1839c1d2a62fbd1d4447f802997896c2b0c0",
            None,
            self.setup_repo,
        )

    def setup_required_packages(self, packages_step):
        packages_step.add_packages(
            [
                "sxhkd",
                "xorg-xrandr",
                "xorg-xinit",
                "xorg-server",
                "nitrogen",
                "picom-ibhagwan-git",
                "dunst",
                "synapse",
            ]
        )

    def setup_required_dotfiles(self, dotfiles_step):
        self._setup_xinitrc(dotfiles_step)
        self._setup_dunstrc(dotfiles_step)
        self._setup_sxhkdrc(dotfiles_step)
        self._setup_picom_config(dotfiles_step)
        self._setup_xresources(dotfiles_step)

    def _setup_xresources(self, dotfiles_step):
        dotfiles_step.add_dotfile_section(
            ".config/Xresources",
            "Theme colors",
            [
                '#include "Xresources.theme"',
                "#define COL_THEME2 #878787",
                "#define COL_THEME3 #555555",
            ],
            file_type=FileType.XResources,
        )
        dotfiles_step.add_dotfile_lines(
            ".config/Xresources.theme",
            ["#define COL_THEME1 #008866"],
            file_type=FileType.XResources,
        )

    def _setup_xinitrc(self, dotfiles_step):
        dotfiles_step.add_dotfile_section(
            ".xinitrc",
            "Basic graphical settings",
            [
                "(sleep 0.1 ; xrandr --output Virtual-1 --mode 1920x1080) &",
                "$LINUX_SETUP_ROOT/steps/graphical_env/set_random_wallpaper.sh &",
                "picom -b --no-fading-openclose --config ~/.config/picom.conf &",
            ],
        )

        dotfiles_step.add_dotfile_section(
            ".xinitrc",
            "Polish keyboard layout",
            ["(sleep 1; setxkbmap pl) &"],
        )
        dotfiles_step.add_dotfile_section(
            ".xinitrc",
            "Notification daemon",
            ["dunst &"],
        )
        dotfiles_step.add_dotfile_section(
            ".xinitrc",
            "Keybindings daemon",
            ["sxhkd &"],
        )
        dotfiles_step.add_dotfile_section(
            ".xinitrc",
            "Screenshot daemon",
            ["flameshot &"],
        )
        dotfiles_step.add_dotfile_section(
            ".xinitrc",
            "App launcher",
            ["(sleep 1; synapse -s) &"],
        )

    def _setup_dunstrc(self, dotfiles_step):
        current_step_dir = Path(__file__).parent

        dotfiles_step.add_dotfile_symlink(
            src=current_step_dir / "dunstrc",
            link=".config/dunst/dunstrc",
            prepend_home_dir_src=False,
            prepend_home_dir_link=True,
        )

    def _setup_sxhkdrc(self, dotfiles_step):
        dotfiles_step.add_dotfile_lines(
            ".config/sxhkd/sxhkdrc",
            [
                "super + shift + {Return, KP_Enter}",
                "    $TERMINAL",
                "",
                "super + shift + {BackSpace, l}",
                "    $LINUX_SETUP_ROOT/steps/graphical_env/shutdown.sh",
                "",
                "{XF86AudioMute, XF86AudioLowerVolume, XF86AudioRaiseVolume}",
                "    $LINUX_SETUP_ROOT/steps/graphical_env/set_volume.sh {0,1,2}",
                "",
                "super + {XF86AudioLowerVolume, XF86AudioRaiseVolume}",
                "    $LINUX_SETUP_ROOT/steps/graphical_env/set_brightness.sh {0,1}",
                "",
                "super + shift + s",
                "    flameshot gui",
                "",
                "super + shift + w",
                "    $LINUX_SETUP_ROOT/steps/graphical_env/set_random_wallpaper.sh",
                "",
                "super + shift + b",
                "    $BROWSER",
                "",
                "super + control + shift + x",
                "    $LINUX_SETUP_ROOT/steps/graphical_env/mount_nice.sh",
            ],
            file_type=FileType.Sxhkd,
        )

    def _setup_picom_config(self, dotfiles_step):
        current_step_dir = Path(__file__).parent

        dotfiles_step.add_dotfile_lines(
            ".config/picom.conf",
            ["corner-radius = 8"],
        )
