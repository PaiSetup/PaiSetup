from steps.step import Step
from utils.services.file_writer import FileType


class ProgrammingNodeStep(Step):
    def __init__(self):
        super().__init__("ProgrammingNode")
        self._npmrc_path = ".config/npm/npmrc"

    def push_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_packages(
            "nodejs",
            "npm",
        )

        home = self._env.home()
        dependency_dispatcher.set_env("Node paths", "NPM_CONFIG_USERCONFIG", f"{home}/{self._npmrc_path}")
        dependency_dispatcher.set_env("Node paths", "NODE_REPL_HISTORY", f"{home}/.local/state/node_repl_history")
        dependency_dispatcher.append_env("Node paths", "PATH", f"{home}/.local/share/npm/bin")

    def perform(self):
        # npm expands ${VAR} references in npmrc by itself
        self._file_writer.write_lines(
            self._npmrc_path,
            [
                "prefix=${XDG_DATA_HOME}/npm",
                "cache=${XDG_CACHE_HOME}/npm",
                "init-module=${XDG_CONFIG_HOME}/npm/config/npm-init.js",
                "logs-dir=${XDG_STATE_HOME}/npm/logs",
            ],
            file_type=FileType.ConfigFile,
        )
