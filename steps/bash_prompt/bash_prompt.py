from steps.step import Step
from pathlib import Path
from steps.dotfiles import FileType


class BashPromptStep(Step):
    def __init__(self):
        super().__init__("Bash prompt")

    def _perform_impl(self):
        pass

    def setup_required_dotfiles(self, dotfiles_step):
        script_path = Path(__file__).parent / "construct_bash_prompt.bash"
        dotfiles_step.add_dotfile_section(
            ".bashrc",
            "Setup bash prompt",
            [
                f"source {script_path}",
            ],
            file_type=FileType.Bash,
        )
