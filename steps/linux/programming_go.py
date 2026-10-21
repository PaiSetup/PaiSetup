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

        home = self._env.home()
        dependency_dispatcher.set_env("Go paths", "GOPATH", f"{home}/.local/share/go")
        dependency_dispatcher.set_env("Go paths", "GOMODCACHE", f"{home}/.cache/go/mod")
        dependency_dispatcher.set_env("Go paths", "GOCACHE", f"{home}/.cache/go-build")
        dependency_dispatcher.set_env("Go paths", "GOBIN", f"{home}/.local/share/go/bin")
