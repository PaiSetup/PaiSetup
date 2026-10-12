from steps.step import Step
from utils.services.file_writer import FileType, LinePlacement


class BashStep(Step):
    def __init__(self):
        super().__init__("Bash")

    def perform(self):
        # Git Bash runs as a login shell, so it only reads .bash_profile. Steps write to .bashrc
        # and .profile, so pull both of them in from there.
        self._file_writer.write_section(
            ".bash_profile",
            "Call .bashrc and .profile, if they exist",
            [
                "[ -f ~/.bashrc ] && . ~/.bashrc",
                "[ -f ~/.profile ] && . ~/.profile",
            ],
            file_type=FileType.Bash,
            line_placement=LinePlacement.End,
        )
