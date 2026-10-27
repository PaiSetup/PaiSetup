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

    def _override_settings(self, settings, statusline_script_path):
        settings = self._setup_settings_model(settings)
        settings = self._setup_settings_default_mode(settings)
        settings = self._setup_settings_statusline(settings, statusline_script_path)
        return settings
