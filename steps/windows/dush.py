from steps.dush_base import DushStepBase
from steps.windows.folders import KnownFolder


class DushStep(DushStepBase):
    def __init__(self, fetch_git):
        super().__init__("Dush", fetch_git)

    def express_dependencies(self, dependency_dispatcher):
        known_folders = dependency_dispatcher.get_known_folders()
        root_dir = known_folders[KnownFolder.Scripts]
        self._projects_dir = known_folders[KnownFolder.Projects]
        self.setup_dush_root_dir(root_dir)

    def perform(self):
        super().perform()
        self._file_writer.write_section(
            ".profile",
            "Developer scripts",
            [
                f'export DUSH_PATH="{self._dush_root_dir}"',
                f'export DUSH_WORKSPACE="{self._projects_dir}"',
                ". $DUSH_PATH/projects/bashies/main.sh",
            ],
        )
