import utils.external_project as ext
from steps.step import Step


class NotesStepBase(Step):
    def __init__(self, name, use_private_notes, notes_dir):
        super().__init__(name)
        self._use_private_notes = use_private_notes
        self._notes_dir = notes_dir

    def perform(self):
        ext.download(
            "git@github.com:DziubanMaciej/Notes.git",
            "master",
            self._notes_dir,
            logger=self._logger,
            fetch=self._flags.strict_download,
        )

        if self._use_private_notes:
            ext.download(
                "git@github.com:DziubanMaciej/NotesPrivate.git",
                "master",
                self._notes_dir / "_prv",
                logger=self._logger,
                fetch=self._flags.strict_download,
            )
