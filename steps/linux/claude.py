import os

from steps.claude.claude_base import ClaudeStepBase
from utils.services.paths import KnownPath


class ClaudeStep(ClaudeStepBase):
    def __init__(self):
        super().__init__()

    def push_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_packages(
            "claude-code",
            "jq",  # used by statusline script
            "libpulse",  # paplay for sound hooks
            "sound-theme-freedesktop",
        )
        dependency_dispatcher.set_env("Claude", "CLAUDE_CONFIG_DIR", self._get_config_dir())

    def perform(self):
        super().perform()

    def _get_config_dir(self):
        return self._paths.get(KnownPath.ConfigHome) / "claude"

    def _override_settings(self, settings, statusline_script_path):
        settings = self._setup_settings_model(settings)
        settings = self._setup_settings_default_mode(settings)
        settings = self._setup_settings_statusline(settings, statusline_script_path)
        settings = self._setup_settings_sound_hooks(settings)
        return settings

    def _setup_settings_sound_hooks(self, settings):
        self._logger.log("Setting sound hooks")
        sound_hook = {
            "matcher": "",
            "hooks": [
                {
                    "type": "command",
                    "command": f"XDG_RUNTIME_DIR=/run/user/{os.getuid()} paplay /usr/share/sounds/freedesktop/stereo/complete.oga",
                }
            ],
        }

        hooks = settings.setdefault("hooks", {})
        for event in ["PermissionRequest", "Stop"]:
            event_hooks = hooks.setdefault(event, [])
            if sound_hook not in event_hooks:
                event_hooks.append(sound_hook)
        return settings
