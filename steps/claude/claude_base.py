import json
from pathlib import Path

from steps.step import Step
from utils.services.file_writer import FileType


class ClaudeStepBase(Step):
    def __init__(self):
        super().__init__("Claude")

    def perform(self):
        config_dir = self._get_config_dir()
        statusline_script_path = config_dir / "statusline.bash"

        self._setup_statusline_script(statusline_script_path)
        self._setup_settings(config_dir, statusline_script_path)

    def _get_config_dir(self):
        raise NotImplementedError()

    def _override_settings(self, settings, statusline_script_path):
        raise NotImplementedError()

    def _setup_statusline_script(self, statusline_script_path):
        self._logger.log("Symlinking statusline script")
        self._file_writer.write_symlink(
            src=Path(__file__).parent / "statusline.bash",
            link=statusline_script_path,
        )

    def _setup_settings(self, config_dir, statusline_script_path):
        settings_path = config_dir / "settings.json"
        if not settings_path.is_file():
            self._logger.push_warning(f"Claude settings file {settings_path} does not exist. Run claude once and rerun setup.")
            return

        with open(settings_path, "r") as file:
            settings = json.load(file)

        with self._logger.indent(f"Patching {settings_path}"):
            settings = self._override_settings(settings, statusline_script_path)

        self._file_writer.write_lines(
            settings_path,
            [json.dumps(settings, indent=2)],
            file_type=FileType.Json,
            skip_recreate=True,
        )

    def _setup_settings_model(self, settings):
        self._logger.log("Setting default model to opus")
        settings["model"] = "opus"
        return settings

    def _setup_settings_default_mode(self, settings):
        self._logger.log("Setting default permission mode to auto")
        settings.setdefault("permissions", {})["defaultMode"] = "auto"
        return settings

    def _setup_settings_statusline(self, settings, statusline_script_path):
        self._logger.log("Setting statusline script")
        settings["statusLine"] = {
            "type": "command",
            "command": f"bash {statusline_script_path.as_posix()}",
        }
        return settings
