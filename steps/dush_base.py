import utils.external_project as ext
from steps.step import Step


class DushStepBase(Step):
    def __init__(self, name):
        super().__init__(name)

    def _get_dush_dir(self):
        raise NotImplementedError()

    def _download_dush(self, dush_dir):
        ext.download(
            "git@github.com:PaiSetup/Dush.git",
            "master",
            dush_dir,
            logger=self._logger,
            fetch=self._flags.strict_download,
        )
