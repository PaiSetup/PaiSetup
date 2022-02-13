from steps.step import Step
from pathlib import Path


class ProgrammingCommonStep(Step):
    def __init__(self):
        super().__init__("Programming common", has_action=False)

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
            "vim",
            "bcompare",
            # System monitoring
            "htop",
            "bmon",
        )
