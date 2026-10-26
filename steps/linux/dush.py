from steps.dush_base import DushStepBase
from utils.services.file_writer import FileType
from utils.services.paths import KnownPath


class DushStep(DushStepBase):
    def __init__(self, fetch_git):
        dush_dir = self._env.home() / "dush"
        super().__init__("Dush", fetch_git, dush_dir)

    def perform(self):
        super().perform()
        self._file_writer.write_section(
            ".bashrc",
            "Developer scripts",
            [
                f'export DUSH_PATH="{self._dush_dir}"',
                f'export DUSH_WORKSPACE="{self._paths.get(KnownPath.Work)}"',
                f'export DUSH_ENABLE_AUTOLOAD="1"',
                ". $DUSH_PATH/dush/framework/frontend.bash",
                ". $DUSH_PATH/dush/projects/bashies/main.sh",
                ". $DUSH_PATH/dush/projects/awsm/main.sh",
                ". $DUSH_PATH/dush/projects/burrito/main.sh",
                ". $DUSH_PATH/dush/projects/pnt/main.sh",
            ],
            file_type=FileType.Bash,
        )

    def push_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_packages(
            "shellcheck-bin",  # needed for sc/scc scripts
        )
        dependency_dispatcher.set_folder_icon(self._dush_dir, "scripts")
        dependency_dispatcher.register_homedir_file(self._dush_dir)
