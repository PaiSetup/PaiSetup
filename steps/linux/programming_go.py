from steps.step import Step
from utils.command import *
from utils.services.paths import KnownPath


class ProgrammingGoStep(Step):
    def __init__(self):
        super().__init__("ProgrammingGo")

    def push_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_packages(
            "go",
            "delve",
        )

        cache_home = self._paths.get(KnownPath.CacheHome)
        dependency_dispatcher.set_env("Go paths", "GOPATH", self._paths.get(KnownPath.DataHome) / "go")
        dependency_dispatcher.set_env("Go paths", "GOMODCACHE", cache_home / "go/mod")
        dependency_dispatcher.set_env("Go paths", "GOCACHE", cache_home / "go-build")
        dependency_dispatcher.set_env("Go paths", "GOBIN", self._paths.get(KnownPath.DataHome) / "go/bin")
