from steps.step import Step
from pathlib import Path
from utils.file_writer import FileType, LinePlacement


class ShellStep(Step):
    def __init__(self, root_dir):
        super().__init__("Shell")
        self._root_dir = root_dir

    def _perform_impl(self):
        self._setup_profile()
        self._setup_bash()

    def _setup_profile(self):
        self._file_writer.write_section(
            ".profile",
            "Some constants",
            [
                f"export LINUX_SETUP_ROOT={self._root_dir}",
                "export EDITOR=vim",
                "export BROWSER=firefox",
                'export BROWSER_PRIVATE="firefox --private-window"',
                "export FILE_MANAGER=thunar",
            ],
        )
        self._file_writer.write_section(
            ".profile",
            "ls aliases",
            [
                "alias ls='ls --color=auto'",
                "alias ll='ls -la'",
                "alias xo='xdg-open'",
            ],
        )
        self._file_writer.write_section(
            ".profile",
            "Move .lesshist file into .config",
            [
                "export LESSHISTFILE=~/.config/lesshst",
            ],
        )

    def _setup_bash(self):
        script_path = Path(__file__).parent / "construct_bash_prompt.bash"
        self._file_writer.write_section(
            ".bashrc",
            "Setup bash prompt",
            [f"source {script_path}"],
            file_type=FileType.Bash,
        )
        self._file_writer.write_section(
            ".bash_profile",
            "Call .bashrc, if it exists",
            ["[ -f ~/.bashrc ] && . ~/.bashrc"],
            file_type=FileType.Bash,
            line_placement=LinePlacement.End,
        )
        self._file_writer.write_section(
            ".bashrc",
            "Infinite history",
            [
                "export HISTFILESIZE=-1",
                "export HISTSIZE=-1",
            ],
            file_type=FileType.Bash,
        )
        self._file_writer.write_section(
            ".bashrc",
            "Call .profile",
            [
                "source ~/.profile",
            ],
            file_type=FileType.Bash,
            line_placement=LinePlacement.End,
        )
