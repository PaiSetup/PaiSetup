import os
from pathlib import Path

import utils.external_project as ext
from steps.step import Step
from utils.keybinding import KeyBinding


class NotesStep(Step):
    def __init__(self, fetch_git):
        super().__init__("notes")
        self.fetch_git = fetch_git
        self._notes_dir = scripts_dir = self._env.home() / "notes"

    def express_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_packages("obsidian")
        dependency_dispatcher.add_keybindings(KeyBinding("t").mod().shift().execute("obsidian e").desc("Obsidian"))
        dependency_dispatcher.set_folder_icon(self._notes_dir, "notes")
        dependency_dispatcher.register_homedir_file(self._notes_dir)

        # Obsidian is an electron app, meaning it uses chromium engine. Chromium engine doesn't properly
        # follow XDG home. See bug: https://bugs.chromium.org/p/chromium/issues/detail?id=1038587
        dependency_dispatcher.register_homedir_file(".pki")

    def register_env_variables(self):
        self._env.set("NOTES_PATH", self._notes_dir)

    def perform(self):
        ext.download(
            "https://github.com/DziubanMaciej/Notes.git",
            "master",
            self._notes_dir,
            logger=self._logger,
            fetch=self.fetch_git,
        )

        self._file_writer.write_section(
            ".config/PaiSetup/xinitrc_base",
            "My personal notes",
            [f'export NOTES_PATH="{self._notes_dir}"'],
        )
