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
