from steps.step import Step
from pathlib import Path
from utils.file_writer import FileType


class ProgrammingCommonStep(Step):
    def __init__(self):
        super().__init__("Programming common")

    def express_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_packages(
            "wget",
            "strace",
            "curl",
            "graphui",  # graphviz
            "man-db",
            "ntfs-3g",
            "xorg-xev",
            # Text editing
            "tmux",
            "nano",
            "vim",
            "bcompare",
            # System monitoring
            "htop",
            "bmon",
        )

    def perform(self):
        # Move .vimrc and .viminfo to ~/.config/vim. There might be more to it when installing extensions, but I don't care now.
        # If anything changes, this seems like a good start: https://vi.stackexchange.com/a/20067
        self._file_writer.write_section(
            ".profile",
            "Move vimrc to .config directory",
            [f'export VIMINIT="source ~/.config/vim/vimrc"'],
        )
        self._file_writer.write_section(
            ".config/vim/vimrc",
            "Move viminfo to ~/.config/vim",
            ["set viminfo+=n~/.config/vim/viminfo"],
            file_type=FileType.Vimrc,
        )

    def register_env_variables(self):
        self._env.set("VIMINIT", "source ~/.vim/vimrc")
