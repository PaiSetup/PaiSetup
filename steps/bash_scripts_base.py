from steps.step import Step
import utils.external_project as ext


class BashScriptsStepBase(Step):
    def __init__(self, name, fetch_git):
        super().__init__(name)
        self._fetch_git = fetch_git

    def setup_scripts_root_dir(self, scripts_root_dir):
        self._scripts_root_dir = scripts_root_dir
        self._scripts_path = self._scripts_root_dir / "BashUtils"

    def perform(self):
        ext.download(
            "https://github.com/InternalMD/Scripts.git",
            "master",
            self._scripts_root_dir,
            logger=self._logger,
            fetch=self._fetch_git,
        )
