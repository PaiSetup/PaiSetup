from steps.notes_base import NotesStepBase
from utils.services.paths import KnownPath


class NotesStep(NotesStepBase):
    def __init__(self, use_private_notes):
        super().__init__("Notes", use_private_notes)

    def _get_notes_dir(self):
        return self._paths.get(KnownPath.Root) / "Notes"

    def push_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_packages("obsidian")

    def perform(self):
        self._download_notes(self._get_notes_dir())
