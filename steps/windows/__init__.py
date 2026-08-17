from steps.ssh import SshStep
from utils.setup_mode import SetupMode

from .activate_windows import ActivateWindowsStep
from .dush import DushStep
from .explorer import ExplorerStep
from .extensions import ExtensionsStep
from .folders import FoldersStep
from .games import GamesStep
from .git import GitStep
from .hw_tools import HwToolsStep
from .icons.icons import IconsStep
from .multimedia_tools import MultimediaToolsStep
from .packages.packages import PackagesStep
from .power import PowerStep
from .privacy import PrivacyStep
from .programming_common import ProgrammingCommonStep
from .programming_cpp import ProgrammingCppStep
from .startup import StartupStep
from .time.time import TimeStep
from .uninstall_bloat import UninstallBloatStep
from .virtualbox import VirtualBoxStep
from .vscode import VscodeStep


class WindowsSetupMode(SetupMode):
    def get_name(self):
        return "windows"

    def get_steps(self, args, root_dir, build_dir, secret_dir, install_packages):
        # TODO-WINDOWS check for admin

        return [
            PackagesStep(build_dir, enable_installation=install_packages, skip_already_installed=True, is_main_machine=True),
            ActivateWindowsStep(secret_dir),
            VscodeStep(build_dir),
            ExplorerStep(),
            ExtensionsStep(),
            HwToolsStep(gaming=True),
            IconsStep(),
            PowerStep(),
            PrivacyStep(),
            TimeStep(),
            StartupStep(),
            UninstallBloatStep(),
            FoldersStep(root_folder="D:\\"),
            DushStep(fetch_git=True),
            GamesStep(),
            GitStep(),
            SshStep(secret_dir, args.full),
            # VirtualBoxStep(), # TODO-WINDOWS broken package
            MultimediaToolsStep(),
            ProgrammingCommonStep(),
            ProgrammingCppStep(False),
        ]


SETUP_MODES = [WindowsSetupMode]
