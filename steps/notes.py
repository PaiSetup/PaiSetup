from steps.step import Step
import utils.external_project as ext
from pathlib import Path
import os


class NotesStep(Step):
    def __init__(self, fetch_git):
        super().__init__("notes")
        self.fetch_git = fetch_git

    def express_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_packages("obsidian")

    def _perform_impl(self):
        notes_dir = scripts_dir = Path(os.environ["HOME"]) / "Notes"
        ext.download(
            "https://github.com/InternalMD/Notes.git",
            "origin/master",
            notes_dir,
            fetch=self.fetch_git,
        )
