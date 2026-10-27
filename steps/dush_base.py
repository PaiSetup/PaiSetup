import utils.external_project as ext
from steps.step import Step


class DushStepBase(Step):
    def __init__(self, name, dush_dir):
        super().__init__(name)
        self._dush_dir = dush_dir

    def perform(self):
        ext.download(
            "git@github.com:PaiSetup/Dush.git",
            "master",
            self._dush_dir,
            logger=self._logger,
            fetch=self._flags.strict_download,
        )
