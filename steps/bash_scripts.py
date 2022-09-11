from steps.step import Step
import utils.external_project as ext
import os
from pathlib import Path


class BashScriptsStep(Step):
    def __init__(self, fetch_git):
        super().__init__("BashScripts")
        self._scripts_root_dir = self._env.home() / "Scripts"
        self._scripts_path = self._scripts_root_dir / "BashUtils"
        self.fetch_git = fetch_git

    def perform(self):
        ext.download(
            "https://github.com/InternalMD/Scripts.git",
            "origin/master",
            self._scripts_root_dir,
            fetch=self.fetch_git,
        )

        self._file_writer.write_section(
            ".profile",
            "Convenience scripts",
            [
                f'export SCRIPTS_PATH="{self._scripts_path}"',
                ". $SCRIPTS_PATH/load_functions.sh",
            ],
        )

    def register_env_variables(self):
        self._env.set("SCRIPTS_PATH", self._scripts_path)

    def express_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_packages("shellcheck")
        dependency_dispatcher.set_folder_icon("Scripts", "scripts")
