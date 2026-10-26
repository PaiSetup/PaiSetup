from steps.step import Step
from utils.command import *
from utils.services.paths import KnownPath


class ProgrammingRustStep(Step):
    def __init__(self):
        super().__init__("ProgrammingRust")

    def push_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_packages("rustup")
        cargo_home = self._paths.get(KnownPath.DataHome) / "cargo"
        dependency_dispatcher.set_env("Rust paths", "CARGO_HOME", cargo_home)
        dependency_dispatcher.set_env("Rust paths", "RUSTUP_HOME", self._paths.get(KnownPath.DataHome) / "rustup")
        dependency_dispatcher.append_env("Rust paths", "PATH", cargo_home / "bin")

    def perform(self):
        run_command("rustup default stable")
