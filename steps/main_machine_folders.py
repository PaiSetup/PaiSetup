from steps.step import Step
import os


class MainMachineFolders(Step):
    def __init__(self):
        super().__init__("MainMachineFolders")
        self._multimedia_dir = self._env.home() / "Multimedia"
        self._work_dir = self._env.home() / "work"

    def express_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.set_folder_icon("Multimedia", "multimedia")
        dependency_dispatcher.set_folder_icon("Multimedia/Avatars", "avatars")
        dependency_dispatcher.set_folder_icon("Multimedia/FreestyleFootball", "football")
        dependency_dispatcher.set_folder_icon("Multimedia/FretSaw", "fretsaw")
        dependency_dispatcher.set_folder_icon("Multimedia/Funny", "funny")
        dependency_dispatcher.set_folder_icon("Multimedia/Icons", "icons")
        dependency_dispatcher.set_folder_icon("Multimedia/Microscope", "microscope")
        dependency_dispatcher.set_folder_icon("Multimedia/Movies", "movies")
        dependency_dispatcher.set_folder_icon("Multimedia/Music", "music")
        dependency_dispatcher.set_folder_icon("Multimedia/MusicToRate", "music")
        dependency_dispatcher.set_folder_icon("Multimedia/TvSeries", "tv_series")
        dependency_dispatcher.set_folder_icon("Multimedia/Wallpapers", "wallpapers")
        dependency_dispatcher.set_folder_icon("work", "work")

    def perform(self):
        self._work_dir.mkdir(parents=True, exist_ok=True)
