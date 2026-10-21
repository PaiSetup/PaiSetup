import re

from steps.step import Step
from utils.dependency_dispatcher import push_dependency_handler
from utils.services.file_writer import FileType, LinePlacement


class EnvStep(Step):
    def __init__(self):
        super().__init__("Env")
        self._sections = {}
        self._names_to_set = set()
        self._names_to_append = set()

    @push_dependency_handler
    def set_env(self, section, name, value):
        value = str(value)

        # Validate.
        if not self._validate_env(name, value):
            return
        if name in self._names_to_set or name in self._names_to_append:
            self._logger.push_warning(f"Ignoring env {name}={value}. Variable was already set.")
            return
        self._names_to_set.add(name)

        # Set in current process, so perform() of other steps can use it before env.sh is sourced.
        self._env.set(name, value, force=True)

        # Save for perform().
        self._sections.setdefault(section, []).append((name, value))

    @push_dependency_handler
    def append_env(self, section, name, value):
        value = str(value)

        # Validate.
        if not self._validate_env(name, value):
            return
        if name in self._names_to_set:
            self._logger.push_warning(f"Ignoring env {name}={value}. Cannot append to a variable that was set.")
            return
        self._names_to_append.add(name)

        # Set in current process, so perform() of other steps can use it before env.sh is sourced.
        self._env.append(name, value)

        # Save for perform().
        #
        # To be fully robust, we write an expression like:
        #    export PATH="${PATH}${PATH:+:}/etc/myRustPath"
        #
        # The second variable is a conditional insertion of a colon, only when previous PATH was not empty and the
        # separator is neccesary. Example expansions:
        #    1. PATH was empty:  "/etc/myRustPath"       (notice there's no colon)
        #    2. PATH was "/bin": "/bin:/etc/myRustPath"  (notice the colon was conditionally inserted)
        self._sections.setdefault(section, []).append((name, f"${{{name}}}${{{name}:+:}}{value}"))

    def _validate_env(self, name, value):
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name):
            self._logger.push_warning(f"Ignoring env {name}={value}. Invalid variable name.")
            return False
        if "$" in value:
            # Values are set in current process verbatim, so they cannot reference other variables.
            self._logger.push_warning(f"Ignoring env {name}={value}. Values cannot reference other variables.")
            return False
        return True

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
