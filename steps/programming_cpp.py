from steps.step import Step
from pathlib import Path


class ProgrammingCppStep(Step):
    def __init__(self, graphics):
        super().__init__("ProgrammingCpp", has_action=False)
        self._graphics = graphics

    def express_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_dotfile_section(
            ".profile",
            "Allow attaching debugger to a running process",
            [
                "echo 0 | sudo tee '/proc/sys/kernel/yama/ptrace_scope' > /dev/null",
            ],
        )
        dependency_dispatcher.add_packages(
            "base-devel",
            "cmake",
            "doxygen",
            "gdb",
            "cgdb",
            "clang-format-all-git",
        )
        if self._graphics:
            dependency_dispatcher.add_packages(
                "vulkan-devel",
                "glm",
                "glfw-x11",
                "renderdoc"
            )
