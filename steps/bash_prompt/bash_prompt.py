from steps.step import Step
from pathlib import Path
from steps.dotfiles import FileType


class BashPromptStep(Step):
    def __init__(self):
        super().__init__("Bash prompt", has_action=False)

    def express_dependencies(self, dependency_dispatcher):
        script_path = Path(__file__).parent / "construct_bash_prompt.bash"
        dependency_dispatcher.add_dotfile_section(
            ".bashrc",
            "Setup bash prompt",
            [
                f"source {script_path}",
            ],
            file_type=FileType.Bash,
        )
