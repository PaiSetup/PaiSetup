from steps.step import Step
from utils import command
from steps.dotfiles import FileType
from pathlib import Path


class GraphicalEnvStep(Step):
    def __init__(self):
        super().__init__("GraphicalEnv")

    def _perform_impl(self):
        pass

    def setup_required_packages(self, packages_step):
        packages_step.add_packages(
            [
                "sxhkd",
                "xorg-xrandr",
                "xorg-xinit",
                "xorg-server",
                "nitrogen",
                "picom",
                "dunst",
            ]
        )

    def setup_required_dotfiles(self, dotfiles_step):
        self._setup_xinitrc(dotfiles_step)
        self._setup_dunstrc(dotfiles_step)
        self._setup_sxhkdrc(dotfiles_step)

    def _setup_xinitrc(self, dotfiles_step):
        dotfiles_step.add_dotfile_section(
            ".xinitrc",
            "Basic graphical settings",
            [
                "(sleep 0.1 ; xrandr --output Virtual-1 --mode 1920x1080) &",
                "(sleep 0.2 ; nitrogen --set-zoom-fill ~/Wallpapers/active) &",
                "picom -b --no-fading-openclose &",
            ],
        )

        dotfiles_step.add_dotfile_section(
            ".xinitrc",
            "Notification daemon",
            ["dunst -config ~/.dunstrc &"],
        )
        dotfiles_step.add_dotfile_section(
            ".xinitrc",
            "Keybindings daemon",
            ["sxhkd &"],
        )

    def _setup_dunstrc(self, dotfiles_step):
        current_step_dir = Path(__file__).parent

        dotfiles_step.add_dotfile_symlink(
            src=current_step_dir / "dunstrc",
            link=".dunstrc",
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
                "    $LINUX_SETUP_ROOT/steps/graphical_env/shutdown.sh 1",
                "super + shift + b",
                "    $BROWSER",
            ],
            file_type=FileType.Sxhkd,
        )
