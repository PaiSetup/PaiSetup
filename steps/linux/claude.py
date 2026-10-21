from steps.step import Step


class ClaudeStep(Step):
    def __init__(self):
        super().__init__("Claude")

    def push_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_packages("claude-code")
        dependency_dispatcher.set_env("Claude", "CLAUDE_CONFIG_DIR", f"{self._env.home()}/.config/claude")
