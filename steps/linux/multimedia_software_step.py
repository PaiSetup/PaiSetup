from pathlib import Path

from steps.step import Step


class MultimediaSoftwareStep(Step):
    def __init__(self):
        super().__init__("MultimediaSoftware")

    def push_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_packages(
            # Video
            "vlc",
            "mpv",
            "obs-studio",  # Recording
            "losslesscut-bin",  # cutting video
            # Images
            "nomacs",
            "qt5-imageformats",  # For webp support in nomacs
            "feh",
            "gimp",
            "imagemagick",  # file conversion
            # Audio
            "rhythmbox",
            "playerctl",
            "gst-plugins-bad",  # Audio plugins
            "gst-plugins-ugly",  # Audio plugins
            # Documents
            "libreoffice-still",
            "qpdfview",
            "pdfsam",
            # Cloud
            "megasync-bin",
            # MTP (for Android phone mounting)
            "gvfs-mtp",
            "gvfs-gphoto2",
            "mtpfs",
            "jmtpfs",
            # Communicators
            "discord",
            # Archives
            "unzip",
            "zip",
            "7zip",
        )
