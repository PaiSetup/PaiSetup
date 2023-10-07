from steps.step import Step
from pathlib import Path
from utils.services.file_writer import FileType


class ProgrammingCommonStep(Step):
    def __init__(self):
        super().__init__("Programming common")

    def express_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_packages(
            "wget",
            "strace",
            "curl",
            "graphui",  # graphviz
            "man-db",
            "ntfs-3g",
            "xorg-xev",
            # Text editing
            "tmux",
            "nano",
            "bcompare",
            # System monitoring
            "htop",
            "bmon",
        )
