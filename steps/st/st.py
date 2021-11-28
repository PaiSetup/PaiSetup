from steps.step import Step
from pathlib import Path
from steps.dotfiles import FileType


class StStep(Step):
    def __init__(self, root_build_dir, setup_repo):
        super().__init__("St")
        self.root_build_dir = root_build_dir
        self.setup_repo = setup_repo

    def _perform_impl(self):
        self._compile_remote_project(
            self.root_build_dir / "st",
            "https://git.suckless.org/st",
            "0.8.4",
            Path(__file__).parent,
            self.setup_repo,
        )

    def setup_required_dotfiles(self, dotfiles_step):
        dotfiles_step.add_dotfile_section(
            ".profile",
            "Command for calling default terminal",
            [
                "export TERMINAL='st -e'",
            ],
        )
        dotfiles_step.add_dotfile_section(
            ".inputrc",
            "Enable DELETE key to work in st",
            ["set enable-keypad on"],
        )
        dotfiles_step.add_dotfile_section(
            ".Xresources",
            "St",
            [
                "st.background: COL_THEME2",
                "st.alpha: 0.6",
            ],
            file_type=FileType.XResources,
        )
