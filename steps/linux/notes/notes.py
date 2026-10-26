from steps.notes_base import NotesStepBase
from utils.keybinding import KeyBinding


class NotesStep(NotesStepBase):
    def __init__(self, fetch_git, use_private_notes):
        notes_dir = self._env.home() / "notes"
        super().__init__("Notes", fetch_git, use_private_notes, notes_dir)

    def push_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_packages("obsidian")
        dependency_dispatcher.add_keybindings(KeyBinding("t").mod().shift().execute("obsidian e").desc("Obsidian"))
        dependency_dispatcher.set_folder_icon(self._notes_dir, "notes")
        dependency_dispatcher.register_homedir_file(self._notes_dir)

        # Obsidian is an electron app, meaning it uses chromium engine. Chromium engine doesn't properly
        # follow XDG home. See bug: https://bugs.chromium.org/p/chromium/issues/detail?id=1038587
        dependency_dispatcher.register_homedir_file(".pki")

        dependency_dispatcher.set_env("My personal notes", "NOTES_PATH", self._notes_dir)

    def register_env_variables(self):
        self._env.set("NOTES_PATH", self._notes_dir)

    def perform(self):
        super().perform()
