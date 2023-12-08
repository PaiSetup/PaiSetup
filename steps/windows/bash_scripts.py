from steps.bash_scripts_base import BashScriptsStepBase
from steps.windows.folders import KnownFolder

class BashScriptsStep(BashScriptsStepBase):
    def __init__(self, fetch_git):
        super().__init__("BashScripts", fetch_git)

    def express_dependencies(self, dependency_dispatcher):
        known_folders = dependency_dispatcher.get_known_folders()
        scripts_root_dir = known_folders[KnownFolder.Scripts]
        self.setup_scripts_root_dir(scripts_root_dir)

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
