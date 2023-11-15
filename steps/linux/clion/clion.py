from steps.step import Step
from pathlib import Path

class ClionStep(Step):
    def __init__(self):
        super().__init__("Clion")
        self._current_step_dir = Path(__file__).parent

    def express_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_packages(
            "clion",
            "clion-jre",
            "clion-gdb",
            "jetbrains-toolbox",
        )


    def perform(self):
        config_dirs = self._find_clion_config_dirs()

        src_file = self._current_step_dir / "keybindings.xml"
        for config_dir in config_dirs:
            dst_file = config_dir / "keymaps" / "XWin copy.xml"
            self._file_writer.write_symlink(src_file, dst_file)

    def _find_clion_config_dirs(self):
        config_dir = self._env.home() / ".config" / "JetBrains"
        result = []
        for subdir in config_dir.iterdir():
            if not subdir.is_dir():
                continue
            dirname = subdir.name
            if "CLion" in dirname:
                result.append(subdir)
        return result
