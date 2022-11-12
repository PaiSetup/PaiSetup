from steps.step import Step
import os


class AudioStep(Step):
    def __init__(self):
        super().__init__("Audio")

    def express_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_packages(
            # Low level alsa
            "alsa-firmware",
            "alsa-utils",
            # Pipewire on top of alsa (replacement for pulseaudio)
            "pipewire-pulse",
            "wireplumber",
            # Utilities for pulseaudio (they also work on pipewire)
            "pamixer",
            "pavucontrol",
        )

    def perform(self):
        self._file_writer.write_section(
            ".config/LinuxSetup/xinitrc_base",
            "Configure pulseaudio modules",
            [
                "pactl unload-module module-suspend-on-idle &",
                "pactl load-module module-switch-on-connect &",
            ],
        )

        self._file_writer.write_lines(
            ".config/pulse/client.conf",
            [
                "autospawn = no",
                "cookie-file = /tmp/pulse-cookie",
            ],
        )
