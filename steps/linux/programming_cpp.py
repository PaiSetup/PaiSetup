from pathlib import Path

from steps.step import Step
from utils.services.file_writer import FileType


class ProgrammingCppStep(Step):
    def __init__(self, graphics, systemc):
        super().__init__("ProgrammingCpp")
        self._graphics = graphics
        self._systemc = systemc

    def push_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_packages(
            "base-devel",
            "cmake",
            "doxygen",
            "gdb",
            "cgdb",
            "clang-format-all-git",
            "valgrind",
        )
        if self._systemc:
            dependency_dispatcher.add_packages(
                "systemc",
                "gtkwave",
            )
        if self._graphics:
            dependency_dispatcher.add_packages(
                "vulkan-devel",
                "glm",
                "glfw",
                "renderdoc-bin",
                "opencl-headers",
            )

        # Author refuses to conform to XDG specification: https://github.com/baldurk/renderdoc/pull/1741.
        # Maybe I could do my own AUR with this PR cherry-pick on top?
        dependency_dispatcher.register_homedir_file(".renderdoc")

    def perform(self):
        self._file_writer.write_lines(
            ".config/gdb/gdbinit",
            [
                "set debuginfod enabled on",
                "tui enable",
                "set history save on",
                "refresh",
                "set tui border-kind space",
                "set tui tab-width 4",
                "set tui compact-source on",
                "focus cmd",
            ],
            file_type=FileType.ConfigFileNoComments,
        )
        (self._env.home() / ".cache/gdb").mkdir(exist_ok=True, parents=True)

        self._file_writer.write_section(
            ".config/PaiSetup/env.sh",
            "GDB paths",
            [
                'export GDBHISTFILE="$HOME/.cache/gdb/history"',
                "export CGDB_DIR=$HOME/.config/cgdb",
            ],
        )

        self._file_writer.write_section(
            ".profile",
            "Allow attaching debugger to a running process",
            [
                "echo 0 | sudo tee '/proc/sys/kernel/yama/ptrace_scope' > /dev/null",
            ],
        )
