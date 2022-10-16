from steps.step import Step
from pathlib import Path
from utils.file_writer import FileType


class ProgrammingCppStep(Step):
    def __init__(self, graphics, systemc):
        super().__init__("ProgrammingCpp")
        self._graphics = graphics
        self._systemc = systemc

    def express_dependencies(self, dependency_dispatcher):
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
                "glfw-x11",
                "renderdoc-bin",
            )

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
            ".profile",
            "Debugger",
            [
                "echo 0 | sudo tee '/proc/sys/kernel/yama/ptrace_scope' > /dev/null #Allow attaching debugger to a running process",
                'export GDBHISTFILE="$HOME/.cache/gdb/history"',
                "export CGDB_DIR=$HOME/.config/cgdb",
            ],
        )
