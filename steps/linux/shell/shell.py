from pathlib import Path

from steps.step import Step
from utils.services.file_writer import FileType, LinePlacement


class ShellStep(Step):
    def __init__(self, root_dir):
        super().__init__("Shell")
        self._root_dir = root_dir

    def push_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_packages(
            "eza",
            "fzf",  # fuzzy search
        )
        dependency_dispatcher.register_homedir_file(".profile")
        dependency_dispatcher.register_homedir_file(".bashrc")
        dependency_dispatcher.register_homedir_file(".bash_logout")
        dependency_dispatcher.register_homedir_file(".bash_profile")

    def perform(self):
        self._setup_profile()
        self._setup_bash()
        self._remove_moved_files()

    def _setup_profile(self):
        self._file_writer.write_section(
            ".profile",
            "Some constants",
            [
                "export EDITOR=nvim",
                "export FILE_MANAGER=thunar",
            ],
        )
        self._file_writer.write_section(
            ".profile",
            "ls aliases",
            [
                "alias ls=eza",
                "alias ll='eza -la'",
                "alias xo='xdg-open'",
                "alias less='less -N'",
            ],
        )
        self._file_writer.write_section(
            ".config/PaiSetup/env.sh",
            "less/wget/yarn paths",
            [
                'export LESSHISTFILE="$XDG_CONFIG_HOME/lesshst"',
                'export WGETRC="$XDG_CONFIG_HOME/wgetrc"',
                "alias yarn='yarn --use-yarnrc \"$XDG_CONFIG_HOME/yarn/config\"'",
            ],
        )
        self._file_writer.write_lines(
            ".config/wgetrc",
            [f"hsts-file={self._env.home()}/.cache/wget-hsts"],
            file_type=FileType.ConfigFile,
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
            "Setup history",
            [
                "export HISTFILESIZE=-1",
                "export HISTSIZE=-1",
                'export HISTFILE="${XDG_STATE_HOME}/bash_history"',
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
        self._file_writer.write_section(
            ".config/PaiSetup/env.sh",
            "Path to inputrc file",
            [
                "export INPUTRC=~/.config/inputrc",
            ],
        )
        self._file_writer.write_section(
            ".config/inputrc",
            "Enable DELETE key to work in terminals",
            ["set enable-keypad on"],
        )

    def _remove_moved_files(self):
        # We set a couple of environment variables to move some dotfiles from ~ to other directories.
        # However, these files may still show up if PaiSetup crashes in the middle and leaves config
        # without the variables. Just remove them.
        files = [
            ".bash_history",
            ".bash_logout",
            ".bash_login",
            ".wget-hsts",
        ]
        for f in files:
            self._file_writer.remove_file(f)
