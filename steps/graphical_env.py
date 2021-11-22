from steps.step import Step
from utils import command
from steps.dotfiles import FileType


class GraphicalEnvStep(Step):
    def __init__(self):
        super().__init__("GraphicalEnv")

    def _perform_impl(self):
        pass

    def setup_required_packages(self, packages_step):
        packages_step.add_packages("sxhkd")

    def setup_required_dotfiles(self, dotfiles_step):
        dotfiles_step.add_dotfile_lines(
            ".xinitrc",
            [
                "sxhkd &",
            ],
        )

        dotfiles_step.add_dotfile_lines(
            ".config/sxhkd/sxhkdrc",
            [
                "super + shift + {Return, KP_Enter}",
                "    $TERMINAL",
                "",
                "super + shift + {BackSpace, l}",
                "    $LINUX_SETUP_ROOT/steps/dwm/dwmblocks/shutdown.sh 1",
                "",
                "super + shift + b",
                "    $BROWSER",
            ],
            file_type=FileType.Sxhkd,
        )
