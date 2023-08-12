from steps.step import Step, dependency_listener
from utils import command
import os
from pathlib import Path
from utils.file_writer import FileType
from utils.log import log


class XsessionStep(Step):
    def __init__(self):
        super().__init__("Xsession")
        self._xsessions = []

    @dependency_listener
    def add_xsession(self, name, xinitrc_path):
        self._xsessions.append((name, xinitrc_path))

    def perform(self):
        for name, xinitrc_path in self._xsessions:
            log(f"Creating a script and .desktop file for {name} session")

            # First create a script that simply calls our xinitrc. Unfortunately we cannot create
            # a reusable script and simply pass an argument in .desktop file, because some DMs
            # (namely LightDM) ignore .desktop files containing arguments to commands.
            script_name = self._file_writer.write_executable_script(
                f"xsession_run_{name}",
                [f'exec "{xinitrc_path}"'],
            )

            # Then create a .desktop file. DMs should scan /usr/share/xsession and allow selecting
            # them in order to launch a specific session.
            self._file_writer.write_lines(
                f"/usr/share/xsessions/{name}.desktop",
                [
                    "[Desktop Entry]",
                    f"Name={name}",
                    f"Comment=Executes {xinitrc_path} script",
                    f"Exec={script_name}",
                    f"TryExec={script_name}",
                    "Type=Application",
                ],
                file_type=FileType.ConfigFile,
            )
