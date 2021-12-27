from steps.step import Step
import os


class AudioStep(Step):
    def __init__(self):
        super().__init__("Audio")
        self.disable_suspending_command = ""

    def setup_required_packages(self, packages_step):
        packages_step.add_packages(
            "alsa-firmware",
            "alsa-utils",
            "pulseaudio",
            "pulseaudio-alsa",
            "pulsemixer",
            "pamixer",
        )

    def setup_required_dotfiles(self, dotfiles_step):
        dotfiles_step.add_dotfile_section(
            ".xinitrc",
            "Unload module-suspend-on-idle from pulseuadio",
            ["pactl unload-module module-suspend-on-idle &"],
        )

    def _perform_impl(self):
        pass
