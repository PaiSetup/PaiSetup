from steps.step import Step


class QBitTorrentStep(Step):
    def __init__(self, has_multimedia_dir):
        super().__init__("QBitTorrent")
        self._has_multimedia_dir = has_multimedia_dir

    def push_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_packages("qbittorrent")

    def perform(self):
        save_paths = [
            self._env.home() / "downloads",
        ]
        # TODO use the same push_dependency as for Thunar?
        if self._has_multimedia_dir:
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
