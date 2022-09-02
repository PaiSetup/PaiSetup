from steps.step import Step
from pathlib import Path
from utils.file_writer import FileType


class BashPromptStep(Step):
    def __init__(self):
        super().__init__("Bash prompt")

    def _perform_impl(self):
        script_path = Path(__file__).parent / "construct_bash_prompt.bash"
        self._file_writer.write_section(
            ".bashrc",
            "Setup bash prompt",
            [f"source {script_path}"],
            file_type=FileType.Bash,
        )
