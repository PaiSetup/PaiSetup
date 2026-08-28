from steps.notes_base import NotesStepBase
from steps.windows.folders import KnownFolder


class NotesStep(NotesStepBase):
    def __init__(self, fetch_git, use_private_notes):
        super().__init__("Notes", fetch_git, use_private_notes)

    def push_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_packages("obsidian")

    def pull_dependencies(self, dependency_dispatcher):
        known_folders = dependency_dispatcher.get_known_folders()
        self.set_notes_root_dir(known_folders[KnownFolder.Notes])
