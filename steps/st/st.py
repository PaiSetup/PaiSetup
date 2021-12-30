from steps.step import Step
from pathlib import Path
from steps.dotfiles import FileType
from utils import command
from utils.log import log


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

        log('Creating "terminal" command to call st')
        command.create_executable_script("terminal", ['st -e \\"\$@\\"'])

    def express_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_dotfile_section(
            ".profile",
            "Command for calling default terminal",
            [
                "export TERMINAL='st -e'",
            ],
        )
        dependency_dispatcher.add_dotfile_section(
            ".profile",
            "Path to inputrc file",
            [
                "export INPUTRC=~/.config/inputrc",
            ],
        )
        dependency_dispatcher.add_dotfile_section(
            ".config/inputrc",
            "Enable DELETE key to work in st",
            ["set enable-keypad on"],
        )
        dependency_dispatcher.add_dotfile_section(
            ".config/Xresources",
            "St",
            [
                "st.background: #222222",
                "st.alpha: 0.6",
                "st.color0:  #282a2e",
                "st.color8:  #373b41",
                "st.color1:  #a54242",
                "st.color9:  #cc6666",
                "st.color2:  #8c9440",
                "st.color10: #b5bd68",
                "st.color3:  #de935f",
                "st.color11: #f0c674",
                "st.color4:  #5f819d",
                "st.color12: #81a2be",
                "st.color5:  #85678f",
                "st.color13: #b294bb",
                "st.color6:  #5e8d87",
                "st.color14: #8abeb7",
                "st.color7:  #b5c2cf",
                "st.color15: #e7eae8",
            ],
            file_type=FileType.XResources,
        )
