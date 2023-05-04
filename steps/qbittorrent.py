from steps.step import Step

class QBitTorrentStep(Step):
    def __init__(self, is_main_machine):
        super().__init__("QBitTorrent")
        self._is_main_machine = is_main_machine

    def express_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_packages("qbittorrent")

    def perform(self):
        save_paths = [
            self._env.home() / "downloads",
        ]
        if self._is_main_machine:
            save_paths += [
                self._env.home() / "multimedia/movies",
                self._env.home() / "multimedia/tv_series",
            ]
        save_paths = [str(x) for x in save_paths]
        save_paths = ', '.join(save_paths)

        self._file_writer.patch_ini_file(
            ".config/qBittorrent/qBittorrent.conf",
            {
                ("AddNewTorrentDialog", "SavePathHistory"): lambda _: save_paths,
            },
        )
