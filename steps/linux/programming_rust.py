from steps.step import Step
from utils.command import *


class ProgrammingRustStep(Step):
    def __init__(self):
        super().__init__("ProgrammingRust")
        self._cargo_home = self._env.home() / ".local/share/cargo"
        self._rustup_home = self._env.home() / ".local/share/rustup"

    def push_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_packages("rustup")
        dependency_dispatcher.set_env("Rust paths", "CARGO_HOME", self._cargo_home)
        dependency_dispatcher.set_env("Rust paths", "RUSTUP_HOME", self._rustup_home)
        dependency_dispatcher.set_env("Rust paths", "PATH", f"${{PATH}}${{PATH:+:}}{self._cargo_home}/bin")

    def register_env_variables(self):
        self._env.set("CARGO_HOME", self._cargo_home)
        self._env.set("RUSTUP_HOME", self._rustup_home)

    def perform(self):
        run_command("rustup default stable")
