from steps.dush_base import DushStepBase
from steps.windows.folders import KnownFolder


class DushStep(DushStepBase):
    def __init__(self, fetch_git):
        super().__init__("Dush", fetch_git)

    def pull_dependencies(self, dependency_dispatcher):
        known_folders = dependency_dispatcher.get_known_folders()
        root_dir = known_folders[KnownFolder.Dush]
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
                f'export DUSH_ENABLE_AUTOLOAD="1"',
                ". $DUSH_PATH/projects/bashies/main.sh",
                ". $DUSH_PATH/projects/yuview/main.sh",
            ],
        )
