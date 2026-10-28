from pathlib import Path

from steps.claude.claude_base import ClaudeStepBase


class ClaudeStep(ClaudeStepBase):
    def __init__(self):
        super().__init__()

    def push_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_packages(
            "claude-code",
            "jq",  # used by statusline script
        )

    def perform(self):
        super().perform()

    def _get_config_dir(self):
        return self._paths.home() / ".claude"

    def _get_sound_command(self):
        sound_path = Path(self._env.get("SystemRoot")) / "Media" / "Windows Proximity Notification.wav"
        return f"powershell -NoProfile -Command \"(New-Object Media.SoundPlayer '{sound_path}').PlaySync()\""
