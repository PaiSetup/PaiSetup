from steps.step import Step
from pathlib import Path
from utils.services.file_writer import FileType
import utils.external_project as ext


class StStep(Step):
    def __init__(self, root_build_dir, fetch_git):
        super().__init__("St")
        self.st_dir = root_build_dir / "st"
        self.fetch_git = fetch_git

    def perform(self):
        current_step_dir = Path(__file__).parent

        ext.download(
            "https://git.suckless.org/st",
            "0.8.4",
            self.st_dir,
            logger=self._logger,
            fetch=self.fetch_git,
            clean=True,
        )
        ext.make(self.st_dir, patches_dir=current_step_dir, logger=self._logger)

        self._logger.log('Creating "terminal" command to call st')
        self._file_writer.write_executable_script("terminal", ['st -e \\"\$@\\"'])

        self._file_writer.write_section(
            ".profile",
            "Command for calling default terminal",
            [
                "export TERMINAL='st -e'",
            ],
        )
        self._file_writer.write_section(
            ".profile",
            "Path to inputrc file",
            [
                "export INPUTRC=~/.config/inputrc",
            ],
        )
        self._file_writer.write_section(
            ".config/inputrc",
            "Enable DELETE key to work in st",
            ["set enable-keypad on"],
        )
        self._file_writer.write_section(
            ".config/XresourcesApp",
            "St",
            [
                "st.background: #222222",
                "st.alpha: 0.92",
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
