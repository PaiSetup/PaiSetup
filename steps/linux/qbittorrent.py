from steps.step import Step
from utils.dependency_dispatcher import push_dependency_handler


class QBitTorrentStep(Step):
    def __init__(self):
        super().__init__("QBitTorrent")
        self._save_paths = [
            self._env.home() / "downloads",
        ]

    def push_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_packages("qbittorrent")

    @push_dependency_handler
    def add_multimedia_directories(self, directories):
        directories = [str(path) for path, _ in directories]
        self._save_paths += directories

    def perform(self):
        paths = [str(x) for x in self._save_paths]
        paths = ", ".join(paths)

        self._file_writer.patch_ini_file(
            ".config/qBittorrent/qBittorrent.conf",
            {
                ("AddNewTorrentDialog", "SavePathHistory"): lambda _: paths,
            },
            must_exist=False,
        )
