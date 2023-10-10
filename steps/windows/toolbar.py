from steps.step import Step
from steps.windows.folders import KnownFolder
from utils.log import log
import pythoncom
from win32com.shell import shell, shellcon


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

    def express_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_packages("windows-handies")

        known_folders = dependency_dispatcher.get_known_folders()
        self._toolbar_dir = known_folders.get(KnownFolder.Toolbar)

    def perform(self):
        if self._toolbar_dir is None:
            self._logger.push_warning("toolbar directory is not set")
            return

        log(f"Cleaning toolbar directory {self._toolbar_dir}")
        for file in self._toolbar_dir.iterdir():
            if file.suffix == ".lnk":
                file.unlink()

        log("Creating link to Powershell window inside PaiSetup")
        self._create_link(
            self._toolbar_dir / "PaiSetupPS.lnk",
            "powershell.exe",
            target_args=f'-NoExit -Command "& {{Set-Location {self._root_dir} }}"',
            as_admin=True,
        )

        log("Creating link to Audioswitch")
        self._create_link(
            self._toolbar_dir / "Audioswitch.lnk",
            "Audioswitch.exe",
        )

        """
        Do we even need this? It may be nice, but I don't like hardcoding the path

        log("Creating link to VSCodium window inside PaiSetup")
        self._create_link(
            self._toolbar_dir / "PaiSetupVSCODE.lnk",
            "D:\\Programs\\VsCodium\\bin\\codium.cmd",
            target_args=str(self._root_dir),
            as_admin=True,
        )
        """

    def _create_link(
        self,
        link_path,
        target_path,
        *,
        target_args=None,
        as_admin=False,
    ):
        """
        Mostly blindly copied from https://stackoverflow.com/a/37063259 and slightly altered.
        """
        link = pythoncom.CoCreateInstance(shell.CLSID_ShellLink, None, pythoncom.CLSCTX_INPROC_SERVER, shell.IID_IShellLink)
        link.SetPath(str(target_path))
        if target_args is not None:
            link.SetArguments(target_args)
        if as_admin:
            link_data = link.QueryInterface(shell.IID_IShellLinkDataList)
            link_data.SetFlags(link_data.GetFlags() | shellcon.SLDF_RUNAS_USER)
        file = link.QueryInterface(pythoncom.IID_IPersistFile)
        file.Save(str(link_path), 0)
