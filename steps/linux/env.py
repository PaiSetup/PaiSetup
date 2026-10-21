import re

from steps.step import Step
from utils.dependency_dispatcher import push_dependency_handler
from utils.services.file_writer import FileType, LinePlacement


class EnvStep(Step):
    def __init__(self):
        super().__init__("Env")
        self._sections = {}

    @push_dependency_handler
    def set_env(self, section, name, value):
        value = str(value)

        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name):
            self._logger.push_warning(f"Ignoring env {name}={value}. Invalid variable name.")
            return
        if re.search(r"\$[A-Za-z]", value):
            # Values are written to both env.sh and environment.d. Use ${NAME}, which works the same way in both.
            self._logger.push_warning(f"Ignoring env {name}={value}. Use ${{NAME}} instead of $NAME.")
            return
        self._sections.setdefault(section, []).append((name, value))

    def perform(self):
        self._setup_env_sh()
        self._setup_environment_d()

    def _setup_env_sh(self):
        self._logger.log("Setting up env.sh")

        # Create env.sh file
        for section, envs in self._sections.items():
            self._file_writer.write_section(
                ".config/PaiSetup/env.sh",
                section,
                [f'export {name}="{value}"' for name, value in envs],
            )

        # Source env.sh file in every init script
        self._file_writer.write_section(
            ".profile",
            "Load environment variables",
            [". ~/.config/PaiSetup/env.sh"],
            line_placement=LinePlacement.Env,
        )
        self._file_writer.write_section(
            ".config/PaiSetup/xinitrc_base",
            "Load environment variables",
            [". ~/.config/PaiSetup/env.sh"],
            line_placement=LinePlacement.Env,
        )
        self._file_writer.write_section(
            ".bashrc",
            "Load environment variables",
            [". ~/.config/PaiSetup/env.sh"],
            line_placement=LinePlacement.Env,
            file_type=FileType.Bash,
        )

    def _setup_environment_d(self):
        self._logger.log("Setting up systemd env config")

        for section, envs in self._sections.items():
            self._file_writer.write_section(
                ".config/environment.d/20-env.conf",
                section,
                [f'{name}="{value}"' for name, value in envs],
                file_type=FileType.ConfigFile,
            )
