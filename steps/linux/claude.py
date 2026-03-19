from steps.step import Step


class ClaudeStep(Step):
    def __init__(self):
        super().__init__("Claude")

    def push_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_packages("claude-code")

    def perform(self):
        self._file_writer.write_section(
            ".config/PaiSetup/env.sh",
            "Claude",
            [
                "export CLAUDE_CONFIG_DIR=$HOME/.config/claude",
            ],
        )
