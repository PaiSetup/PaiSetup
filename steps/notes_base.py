import utils.external_project as ext
from steps.step import Step


class NotesStepBase(Step):
    def __init__(self, name, use_private_notes):
        super().__init__(name)
        self._use_private_notes = use_private_notes

    def _get_notes_dir(self):
        raise NotImplementedError()

    def _download_notes(self, notes_dir):
        ext.download(
            "git@github.com:DziubanMaciej/Notes.git",
            "master",
            notes_dir,
            logger=self._logger,
            fetch=self._flags.strict_download,
        )

        if self._use_private_notes:
            ext.download(
                "git@github.com:DziubanMaciej/NotesPrivate.git",
                "master",
                notes_dir / "_prv",
                logger=self._logger,
                fetch=self._flags.strict_download,
            )
