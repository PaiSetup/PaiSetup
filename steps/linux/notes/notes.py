from steps.notes_base import NotesStepBase
from utils.keybinding import KeyBinding


class NotesStep(NotesStepBase):
    def __init__(self, use_private_notes):
        super().__init__("Notes", use_private_notes)

    def _get_notes_dir(self):
        return self._paths.home() / "notes"

    def push_dependencies(self, dependency_dispatcher):
        notes_dir = self._get_notes_dir()

        dependency_dispatcher.add_packages("obsidian")
        dependency_dispatcher.add_keybindings(KeyBinding("t").mod().shift().execute("obsidian e").desc("Obsidian"))
        dependency_dispatcher.set_folder_icon(notes_dir, "notes")
        dependency_dispatcher.register_homedir_file(notes_dir)

        # Obsidian is an electron app, meaning it uses chromium engine. Chromium engine doesn't properly
        # follow XDG home. See bug: https://bugs.chromium.org/p/chromium/issues/detail?id=1038587
        dependency_dispatcher.register_homedir_file(".pki")

        dependency_dispatcher.set_env("My personal notes", "NOTES_PATH", notes_dir)

    def perform(self):
        self._download_notes(self._get_notes_dir())
