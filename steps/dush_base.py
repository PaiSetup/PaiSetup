import utils.external_project as ext
from steps.step import Step


class DushStepBase(Step):
    def __init__(self, name, fetch_git):
        super().__init__(name)
        self._fetch_git = fetch_git

    def setup_dush_root_dir(self, root_dir):
        self._dush_root_dir = root_dir

    def perform(self):
        ext.download(
            "git@github.com:PaiSetup/Dush.git",
            "master",
            self._dush_root_dir,
            logger=self._logger,
            fetch=self._fetch_git,
        )
