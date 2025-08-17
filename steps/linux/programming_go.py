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
        self._file_writer.write_section(
            ".config/PaiSetup/env.sh",
            "Go paths",
            [
                'export GOPATH="$XDG_DATA_HOME/go"',
                'export GOMODCACHE="$XDG_CACHE_HOME/go/mod"',
            ],
        )
