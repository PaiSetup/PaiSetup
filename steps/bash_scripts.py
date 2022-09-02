from steps.step import Step
import utils.external_project as ext
import os
from pathlib import Path


class BashScriptsStep(Step):
    def __init__(self, fetch_git):
        super().__init__("BashScripts")
        self.scripts_dir = scripts_dir = Path(os.environ["HOME"]) / "Scripts"
        self.fetch_git = fetch_git

    def _perform_impl(self):
        ext.download(
            "https://github.com/InternalMD/Scripts.git",
            "origin/master",
            self.scripts_dir,
            fetch=self.fetch_git,
        )

        self._file_writer.write_section(
            ".profile",
            "Convenience scripts",
            [
                f'export SCRIPTS_PATH="{self.scripts_dir}/BashUtils"',
                ". $SCRIPTS_PATH/load_functions.sh",
            ],
        )

    def express_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_packages("shellcheck")
