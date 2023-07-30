from steps.step import Step
from utils import command


class ProgrammingRustStep(Step):
    def __init__(self):
        super().__init__("ProgrammingRust")
        self._cargo_home = self._env.home() / ".local/share/cargo"
        self._rustup_home = self._env.home() / ".local/share/rustup"

    def express_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_packages("rustup")

    def register_env_variables(self):
        self._env.set("CARGO_HOME", self._cargo_home)
        self._env.set("RUSTUP_HOME", self._rustup_home)

    def perform(self):
        command.run_command("rustup default stable")

        rust_config = [
            f'export CARGO_HOME="{self._cargo_home}"',
            f'export RUSTUP_HOME="{self._rustup_home}"',
            f'export PATH="$PATH:{self._cargo_home}/bin"',
        ]

        self._file_writer.write_section(
            ".config/PaiSetup/xinitrc_base",
            "Configure rust",
            rust_config,
        )

        # Needed for VSCode, which seems to clear variables from xinitrc
        self._file_writer.write_section(
            ".profile",
            "Configure rust",
            rust_config,
        )
