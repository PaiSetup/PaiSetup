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

    def _get_sound_command(self):
        return f"XDG_RUNTIME_DIR=/run/user/{os.getuid()} paplay /usr/share/sounds/freedesktop/stereo/complete.oga"
