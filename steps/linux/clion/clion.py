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
        src_config_dir = self._current_step_dir / "config"

        config_dirs = self._find_clion_config_dirs()
        if config_dirs:
            for config_dir in config_dirs:
                self._symlink_config_files(src_config_dir, config_dir)
        else:
            self._logger.push_warning("No CLion configs found")

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

    def _symlink_config_files(self, src_config_dir, dst_config_dir):
        files = Path(src_config_dir).glob("**/*")
        files = [x for x in files if x.is_file()]
        files = list(files)

        self._logger.log(f"Symlinking {len(files)} for {dst_config_dir.name}")
        for src_file in files:
            dst_file = src_file.relative_to(src_config_dir)
            dst_file = dst_config_dir / dst_file
            self._file_writer.write_symlink(src_file, dst_file)
