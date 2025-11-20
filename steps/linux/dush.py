from steps.dush_base import DushStepBase


class DushStep(DushStepBase):
    def __init__(self, fetch_git):
        super().__init__("Dush", fetch_git)
        self.setup_dush_root_dir(self._env.home() / "dush")

    def perform(self):
        super().perform()
        self._file_writer.write_section(
            ".profile",
            "Developer scripts",
            [
                f'export DUSH_PATH="{self._dush_root_dir}"',
                f'export DUSH_WORKSPACE="$HOME/work"',
                f'export DUSH_ENABLE_AUTOLOAD="1"',
                ". $DUSH_PATH/framework/frontend.bash",
                ". $DUSH_PATH/projects/bashies/main.sh",
                ". $DUSH_PATH/projects/awsm/main.sh",
            ],
        )

    def register_env_variables(self):
        self._env.set("DUSH_PATH", self._dush_root_dir)
        self._env.set("DUSH_WORKSPACE", self._env.home() / "work")

    def push_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_packages(
            "shellcheck-bin",  # needed for sc/scc scripts
        )
        dependency_dispatcher.set_folder_icon(self._dush_root_dir, "scripts")
        dependency_dispatcher.register_homedir_file(self._dush_root_dir)
