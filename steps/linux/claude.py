from steps.step import Step
from utils.services.paths import KnownPath


class ClaudeStep(Step):
    def __init__(self):
        super().__init__("Claude")

    def push_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_packages("claude-code")
        dependency_dispatcher.set_env("Claude", "CLAUDE_CONFIG_DIR", self._paths.get(KnownPath.ConfigHome) / "claude")
