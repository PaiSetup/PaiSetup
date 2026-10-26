from steps.notes_base import NotesStepBase
from utils.services.paths import KnownPath


class NotesStep(NotesStepBase):
    def __init__(self, fetch_git, use_private_notes, notes_dir=None):
        super().__init__("Notes", fetch_git, use_private_notes, notes_dir)

    def push_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_packages("obsidian")

    def perform(self):
        if self._notes_dir is None:
            self._notes_dir = self._paths.get(KnownPath.Root) / "Notes"
        super().perform()
