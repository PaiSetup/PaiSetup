from steps.step import Step
from steps.windows.folders import KnownFolder
from utils.windows.shortcut import create_shortcut


class ToolbarStep(Step):
    """
    This step creates shortcuts in toolbar directory, but it doesn't add the toolbar
    to the taskbar. There is no API for it. It might be possible to reverse engineer
    the binary in HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Streams\Desktop,
    but the ROI is quite low.
    """

    def __init__(self, root_dir):
        super().__init__("Toolbar")
        self._root_dir = root_dir

    def push_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_packages("windows-handies")

    def pull_dependencies(self, dependency_dispatcher):
        known_folders = dependency_dispatcher.get_known_folders()
        self._toolbar_dir = known_folders.get(KnownFolder.Toolbar)

    def perform(self):
        if self._toolbar_dir is None:
            self._logger.push_warning("toolbar directory is not set")
            return

        self._logger.log(f"Cleaning toolbar directory {self._toolbar_dir}")
        for file in self._toolbar_dir.iterdir():
            if file.suffix == ".lnk":
                file.unlink()

        self._logger.log("Creating link to Powershell window inside PaiSetup")
        create_shortcut(
            self._toolbar_dir / "PaiSetupPS.lnk",
            "powershell.exe",
            target_args=f'-NoExit -Command "& {{Set-Location {self._root_dir} }}"',
            as_admin=True,
        )

        self._logger.log("Creating link to Audioswitch")
        create_shortcut(
            self._toolbar_dir / "Audioswitch.lnk",
            "Audioswitch.exe",
        )

        """
        Do we even need this? It may be nice, but I don't like hardcoding the path

        self._logger.log("Creating link to VSCodium window inside PaiSetup")
        create_shortcut(
            self._toolbar_dir / "PaiSetupVSCODE.lnk",
            "D:\\Programs\\VsCodium\\bin\\codium.cmd",
            target_args=str(self._root_dir),
            as_admin=True,
        )
        """
