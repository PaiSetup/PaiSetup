from steps.step import Step
import os


class AudioStep(Step):
    def __init__(self):
        super().__init__("Audio")
        self.disable_suspending_command = ""

    def express_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_packages(
            "alsa-firmware",
            "alsa-utils",
            "pulseaudio",
            "pulseaudio-alsa",
            "pulsemixer",
            "pamixer",
        )

    def _perform_impl(self):
        self._file_writer.write_section(
            ".config/LinuxSetup/xinitrc_base",
            "Unload module-suspend-on-idle from pulseuadio",
            ["pactl unload-module module-suspend-on-idle &"],
        )
