import json
from pathlib import Path

from steps.step import Step
from utils.services.file_writer import FileType


class ClaudeStepBase(Step):
    def __init__(self):
        super().__init__("Claude")

    def perform(self):
        config_dir = self._get_config_dir()
        if not config_dir.is_dir():
            self._logger.push_warning(f"Claude config dir {config_dir} does not exist. Run claude once and rerun setup.")
            return

        statusline_link_path = config_dir / "statusline.bash"

        self._setup_statusline_script(statusline_link_path)
        self._setup_settings(config_dir, statusline_link_path)

    def _get_config_dir(self):
        raise NotImplementedError()

    def _get_statusline_script_path(self):
        return Path(__file__).parent / "statusline.bash"

    def _get_sound_command(self):
        raise NotImplementedError()

    def _setup_statusline_script(self, statusline_link_path):
        self._logger.log("Symlinking statusline script")
        self._file_writer.write_symlink(
            src=self._get_statusline_script_path(),
            link=statusline_link_path,
        )

    def _setup_settings(self, config_dir, statusline_link_path):
        settings_path = config_dir / "settings.json"
        if not settings_path.is_file():
            self._logger.push_warning(f"Claude settings file {settings_path} does not exist. Run claude once and rerun setup.")
            return

        with open(settings_path, "r") as file:
            settings = json.load(file)

        with self._logger.indent(f"Patching {settings_path}"):
            settings = self._override_settings(settings, statusline_link_path)

        self._file_writer.write_lines(
            settings_path,
            [json.dumps(settings, indent=2)],
            file_type=FileType.Json,
            skip_recreate=True,
        )

    def _override_settings(self, settings, statusline_link_path):
        settings = self._setup_settings_model(settings)
        settings = self._setup_settings_default_mode(settings)
        settings = self._setup_settings_statusline(settings, statusline_link_path)
        settings = self._setup_settings_idle_compaction(settings)
        settings = self._setup_settings_sound_hooks(settings)
        return settings

    def _setup_settings_model(self, settings):
        self._logger.log("Setting default model to opus")
        settings["model"] = "opus"
        return settings

    def _setup_settings_default_mode(self, settings):
        self._logger.log("Setting default permission mode to auto")
        settings.setdefault("permissions", {})["defaultMode"] = "auto"
        return settings

    def _setup_settings_statusline(self, settings, statusline_link_path):
        self._logger.log("Setting statusline script")
        settings["statusLine"] = {
            "type": "command",
            "command": f"bash {statusline_link_path.as_posix()}",
        }
        return settings

    def _setup_settings_idle_compaction(self, settings):
        self._logger.log("Disabling idle compaction")
        settings["idleCompaction"] = False
        return settings

    def _setup_settings_sound_hooks(self, settings):
        self._logger.log("Setting sound hooks")
        sound_hook = {
            "matcher": "",
            "hooks": [
                {
                    "type": "command",
                    "command": self._get_sound_command(),
                }
            ],
        }

        hooks = settings.setdefault("hooks", {})
        for event in ["PermissionRequest", "Stop"]:
            event_hooks = hooks.setdefault(event, [])
            if sound_hook not in event_hooks:
                event_hooks.append(sound_hook)
        return settings
