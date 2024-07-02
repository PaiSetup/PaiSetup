from steps.bash_scripts_base import BashScriptsStepBase


class BashScriptsStep(BashScriptsStepBase):
    def __init__(self, fetch_git):
        super().__init__("BashScripts", fetch_git)
        self.setup_scripts_root_dir(self._env.home() / "scripts")

    def perform(self):
        super().perform()
        self._file_writer.write_section(
            ".profile",
            "Convenience scripts",
            [
                f'export SCRIPTS_PATH="{self._scripts_path}"',
                ". $SCRIPTS_PATH/load_functions.sh",
            ],
        )

    def register_env_variables(self):
        self._env.set("SCRIPTS_PATH", self._scripts_path)

    def express_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_packages(
            "shellcheck",
            "python-music-tag",  # Needed by music_tagger.py
        )
        dependency_dispatcher.set_folder_icon(self._scripts_root_dir, "scripts")
        dependency_dispatcher.register_homedir_file(self._scripts_root_dir)

        ftag_path = f"{self._scripts_root_dir}/ftag/ftag"
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
