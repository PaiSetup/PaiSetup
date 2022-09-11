from steps.step import Step
import os


class MainMachineFolders(Step):
    def __init__(self):
        super().__init__("MainMachineFolders")
        self._multimedia_dir = self._env.home() / "Multimedia"
        self._work_dir = self._env.home() / "work"

    def express_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.set_folder_icon(self._multimedia_dir, "multimedia")
        dependency_dispatcher.set_folder_icon(self._multimedia_dir / "Avatars", "avatars")
        dependency_dispatcher.set_folder_icon(self._multimedia_dir / "FreestyleFootball", "football")
        dependency_dispatcher.set_folder_icon(self._multimedia_dir / "FretSaw", "fretsaw")
        dependency_dispatcher.set_folder_icon(self._multimedia_dir / "Funny", "funny")
        dependency_dispatcher.set_folder_icon(self._multimedia_dir / "Icons", "icons")
        dependency_dispatcher.set_folder_icon(self._multimedia_dir / "Microscope", "microscope")
        dependency_dispatcher.set_folder_icon(self._multimedia_dir / "Movies", "movies")
        dependency_dispatcher.set_folder_icon(self._multimedia_dir / "Music", "music")
        dependency_dispatcher.set_folder_icon(self._multimedia_dir / "MusicToRate", "music")
        dependency_dispatcher.set_folder_icon(self._multimedia_dir / "TvSeries", "tv_series")
        dependency_dispatcher.set_folder_icon(self._multimedia_dir / "Wallpapers", "wallpapers")
        dependency_dispatcher.set_folder_icon(self._work_dir, "work")

    def perform(self):
        self._work_dir.mkdir(parents=True, exist_ok=True)
