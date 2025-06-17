from pathlib import Path

from steps.step import Step


class ProgrammingCommonStep(Step):
    def __init__(self):
        super().__init__("Programming common")

    def push_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_packages(
            "wget",
            "strace",
            "curl",
            "man-db",
            "ntfs-3g",
            "dos2unix",
            "nmap",
            "bc",
            # Text editing
            "tmux",
            "nano",
            "bcompare",
            # System monitoring
            "htop",
            "bmon",
        )
