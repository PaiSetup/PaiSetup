from steps.step import Step
import os


class MainMachineFolders(Step):
    def __init__(self):
        super().__init__("MainMachineFolders")
        self._multimedia_dir = self._env.home() / "multimedia"
        self._work_dir = self._env.home() / "work"

    def express_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.set_folder_icon(self._multimedia_dir, "multimedia")
        dependency_dispatcher.set_folder_icon(self._multimedia_dir / "avatars", "avatars")
        dependency_dispatcher.set_folder_icon(self._multimedia_dir / "freestyle_football", "football")
        dependency_dispatcher.set_folder_icon(self._multimedia_dir / "fret_saw", "fretsaw")
        dependency_dispatcher.set_folder_icon(self._multimedia_dir / "funny", "funny")
        dependency_dispatcher.set_folder_icon(self._multimedia_dir / "icons", "icons")
        dependency_dispatcher.set_folder_icon(self._multimedia_dir / "microscope", "microscope")
        dependency_dispatcher.set_folder_icon(self._multimedia_dir / "movies", "movies")
        dependency_dispatcher.set_folder_icon(self._multimedia_dir / "music", "music")
        dependency_dispatcher.set_folder_icon(self._multimedia_dir / "music_to_rate", "music")
        dependency_dispatcher.set_folder_icon(self._multimedia_dir / "tv_series", "tv_series")
        dependency_dispatcher.set_folder_icon(self._multimedia_dir / "wallpapers", "wallpapers")
        dependency_dispatcher.set_folder_icon(self._work_dir, "work")

    def perform(self):
        self._work_dir.mkdir(parents=True, exist_ok=True)
