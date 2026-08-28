import utils.external_project as ext
from steps.step import Step


class NotesStepBase(Step):
    def __init__(self, name, fetch_git, use_private_notes):
        super().__init__(name)
        self._fetch_git = fetch_git
        self._use_private_notes = use_private_notes

    def set_notes_root_dir(self, notes_dir):
        self._notes_dir = notes_dir

    def perform(self):
        ext.download(
            "git@github.com:DziubanMaciej/Notes.git",
            "master",
            self._notes_dir,
            logger=self._logger,
            fetch=self._fetch_git,
        )

        if self._use_private_notes:
            ext.download(
                "git@github.com:DziubanMaciej/NotesPrivate.git",
                "master",
                self._notes_dir / "_prv",
                logger=self._logger,
                fetch=self._fetch_git,
            )
