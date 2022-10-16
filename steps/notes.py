from steps.step import Step
import utils.external_project as ext
from pathlib import Path
import os
from utils.keybinding import KeyBinding


class NotesStep(Step):
    def __init__(self, fetch_git):
        super().__init__("notes")
        self.fetch_git = fetch_git
        self._notes_dir = scripts_dir = self._env.home() / "notes"

    def express_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_packages("obsidian")
        dependency_dispatcher.add_keybindings(KeyBinding("t").mod().shift().execute("obsidian e"))
        dependency_dispatcher.set_folder_icon(self._notes_dir, "notes")

    def register_env_variables(self):
        self._env.set("NOTES_PATH", self._notes_dir)

    def perform(self):
        ext.download(
            "https://github.com/InternalMD/Notes.git",
            "master",
            self._notes_dir,
            fetch=self.fetch_git,
        )

        self._file_writer.write_section(
            ".config/LinuxSetup/xinitrc_base",
            "My personal notes",
            [f'export NOTES_PATH="{self._notes_dir}"'],
        )
