from steps.step import Step
import utils.external_project as ext
from pathlib import Path
import os
from utils.keybinding import KeyBinding


class NotesStep(Step):
    def __init__(self, fetch_git):
        super().__init__("notes")
        self.fetch_git = fetch_git

    def express_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_packages("obsidian")
        dependency_dispatcher.add_keybindings(
            KeyBinding('t').mod().shift().execute("obsidian e")
        )
        dependency_dispatcher.set_folder_icon("Notes", "notes")

    def perform(self):
        notes_dir = scripts_dir = self._env.home() / "Notes"
        ext.download(
            "https://github.com/InternalMD/Notes.git",
            "master",
            notes_dir,
            fetch=self.fetch_git,
        )
