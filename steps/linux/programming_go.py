from steps.step import Step
from utils.command import *


class ProgrammingGoStep(Step):
    def __init__(self):
        super().__init__("ProgrammingGo")

    def push_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_packages(
            "go",
            "delve",
        )

    def perform(self):
        home = self._env.home()
        self._file_writer.write_lines(
            ".config/environment.d/20-go.conf",
            [
                f"GOPATH={home}/.local/share/go",
                f"GOMODCACHE={home}/.cache/go/mod",
                f"GOCACHE={home}/.cache/go-build",
                f"GOBIN={home}/.local/share/go/bin",
            ],
        )
