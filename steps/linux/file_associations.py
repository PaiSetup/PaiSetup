import os

from steps.step import Step
from utils.command import *


class FileAssociationsStep(Step):
    def __init__(self):
        super().__init__("FileAssociations")

    def perform(self):
        image_mimes = [
            "image/bmp",
            "image/cgm",
            "image/g",
            "image/gif",
            "image/ief",
            "image/jpeg",
            "image/ktx",
            "image/png",
            "image/prs.btif",
            "image/svg+xml",
            "image/tiff",
            "image/vnd.adobe.photoshop",
            "image/vnd.dece.graphic",
            "image/vnd.djvu",
            "image/vnd.dvb.subtitle",
            "image/vnd.dwg",
            "image/vnd.dxf",
            "image/vnd.fastbidsheet",
            "image/vnd.fpx",
            "image/vnd.fst",
            "image/vnd.fujixerox.edmics-mmr",
            "image/vnd.fujixerox.edmics-rlc",
            "image/vnd.ms-modi",
            "image/vnd.net-fpx",
            "image/vnd.wap.wbmp",
            "image/vnd.xiff",
            "image/webp",
            "image/x-cmu-raster",
            "image/x-cmx",
            "image/x-freehand",
            "image/x-icon",
            "image/x-pcx",
            "image/x-pict",
            "image/x-portable-anymap",
            "image/x-portable-bitmap",
            "image/x-portable-graymap",
            "image/x-portable-pixmap",
            "image/x-rgb",
            "image/x-xbitmap",
            "image/x-xpixmap",
            "image/x-xwindowdump",
        ]

        video_mimes = [
            "video/h",
            "video/jpeg",
            "video/jpm",
            "video/mj",
            "video/mp",
            "video/mp4",
            "video/mpeg",
            "video/x-matroska",
            "video/ogg",
            "video/quicktime",
            "video/vnd.dece.hd",
            "video/vnd.dece.mobile",
            "video/vnd.dece.pd",
            "video/vnd.dece.sd",
            "video/vnd.dece.video",
            "video/vnd.fvt",
            "video/vnd.mpegurl",
            "video/vnd.ms-playready.media.pyv",
            "video/vnd.uvvu.mp",
            "video/vnd.vivo",
            "video/webm",
            "video/x-f",
            "video/x-fli",
            "video/x-flv",
            "video/x-m",
            "video/x-ms-asf",
            "video/x-msvideo",
            "video/x-ms-wm",
            "video/x-ms-wmv",
            "video/x-ms-wmx",
            "video/x-ms-wvx",
            "video/x-sgi-movie",
        ]

        audio_mimes = [
            "audio/adpcm",
            "audio/basic",
            "audio/midi",
            "audio/mp",
            "audio/mpeg",
            "audio/ogg",
            "audio/vnd.dece.audio",
            "audio/vnd.digital-winds",
            "audio/vnd.dra",
            "audio/vnd.dts",
            "audio/vnd.dts.hd",
            "audio/vnd.lucent.voice",
            "audio/vnd.ms-playready.media.pya",
            "audio/vnd.nuera.ecelp",
            "audio/vnd.rip",
            "audio/webm",
            "audio/x-aac",
            "audio/x-aiff",
            "audio/x-mpegurl",
            "audio/x-ms-wax",
            "audio/x-ms-wma",
            "audio/x-pn-realaudio",
            "audio/x-pn-realaudio-plugin",
            "audio/x-wav",
        ]

        music_mimes = [
            "audio/mp3",
            "audio/flac",
        ]

        pdf_mimes = [
            "application/pdf",
        ]

        text_types = [
            "text/plain",
            "application/json",
            "text/x-c",
            "text/x-diff",
            "text/x-makefile",
            "text/xml",
            "text/x-perl",
            "text/x-shellscript",
            "text/csv",
        ]

        associations = [
            ("thunar.desktop", "inode/directory"),
            ("vlc.desktop", video_mimes + audio_mimes),
            ("org.gnome.Rhythmbox3.desktop", music_mimes),
            ("org.nomacs.ImageLounge.desktop", image_mimes),
            ("qpdfview.desktop", pdf_mimes),
            # ("terminal_nvim.desktop", text_types),
            ("code-oss.desktop", text_types),
        ]

        # Check available .desktop files with following command:
        #   sudo find /usr/share/applications
        # Check mime type of a given file with following command:
        #    xdg-mime query filetype "file"
        # Check default app of a given file with following command:
        #    xdg-mime query default "$(xdg-mime query filetype "file")"

        for application, mime_types in associations:
            self._logger.log(f"Associating {len(mime_types)} with {application}")

            # This command will update ~/.config/mimeapps.list file
            run_command(f"xdg-mime default {application} {' '.join(mime_types)}")
