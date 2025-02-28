from pathlib import Path

from steps.step import Step
from utils.services.file_writer import FileType


class ProgrammingCommonStep(Step):
    def __init__(self):
        super().__init__("Programming common")

    def push_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_packages(
            "wget",
            "strace",
            "curl",
            "graphui",  # graphviz
            "man-db",
            "ntfs-3g",
            "xorg-xev",
            "xclip",
            # Text editing
            "tmux",
            "nano",
            "bcompare",
            # System monitoring
            "htop",
            "bmon",
        )
