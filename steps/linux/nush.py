import utils.external_project as ext
from steps.step import Step


class NushStep(Step):
    def __init__(self, fetch_git):
        super().__init__("Nush")
        self._nush_root_dir = self._env.home() / "nush"
        self._fetch_git = fetch_git

    def perform(self):
        ext.download(
            "https://github.com/PaiSetup/Nush.git",
            "master",
            self._nush_root_dir,
            logger=self._logger,
            fetch=self._fetch_git,
        )

    def express_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_packages(
            "python-music-tag",  # Needed by music_tagger.py
            "python-pytz",  # Needed by size_fixer.py
            "exiv2",  # Needed by size_fixer.py
        )
        dependency_dispatcher.set_folder_icon(self._nush_root_dir, "scripts")
        dependency_dispatcher.register_homedir_file(self._nush_root_dir)

        ftag_path = f"{self._nush_root_dir}/ftag/ftag"
        dependency_dispatcher.add_thunar_custom_action(
            {
                "name": "ftag: tag a file",
                "command": f'st -e sh -c "{ftag_path} --file %F"',
                "image-files": None,
                "video-files": None,
            }
        )
        dependency_dispatcher.add_thunar_custom_action(
            {
                "name": "ftag: generate symlinks",
                "command": f'st -e sh -c "{ftag_path} --generate"',
                "directories": None,
            }
        )
        dependency_dispatcher.add_thunar_custom_action(
            {
                "name": "ftag: tag all",
                "command": f'st -e sh -c "{ftag_path} --tag_all"',
                "directories": None,
            }
        )
        dependency_dispatcher.add_thunar_custom_action(
            {
                "name": "ftag: create query",
                "command": f'st -e sh -c "{ftag_path} --create_query"',
                "directories": None,
            }
        )
