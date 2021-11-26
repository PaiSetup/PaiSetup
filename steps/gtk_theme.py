from steps.step import Step
from utils import command
import os


class GtkThemeStep(Step):
    def __init__(self):
        super().__init__("GtkTheme")

    def _perform_impl(self):
        theme_name = "Layan"
        with open(f"{os.environ['HOME']}/.config/gtk-3.0/settings.ini", "w") as settings_file:
            settings_file.writelines(
                [
                    f"[Settings]\n",
                    f"gtk-theme-name={theme_name}\n",
                ]
            )

    def setup_required_packages(self, packages_step):
        packages_step.add_packages("layan-gtk-theme-git")
