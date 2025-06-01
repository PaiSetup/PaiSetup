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
from .toolbar import ToolbarStep
from .uninstall_bloat import UninstallBloatStep
from .virtualbox import VirtualBoxStep
from .vscode import VscodeStep


def get_steps(args, root_dir, build_dir, secret_dir, install_packages):
    match args.mode:
        case SetupMode.windows:
            is_normie = False
        case SetupMode.windows_normie:
            is_normie = True
        case _:
            raise ValueError("Selected SetupMode is unsupported for Windows")

    # TODO check for admin

    # Add default steps
    steps = [
        PackagesStep(build_dir, skip_already_installed=True, is_main_machine=not is_normie),
        ActivateWindowsStep(secret_dir),
        ExplorerStep(),
        ExtensionsStep(),
        HwToolsStep(gaming=True),
        IconsStep(),
        PowerStep(),
        PrivacyStep(),
        TimeStep(),
        StartupStep(),
        UninstallBloatStep(),
        VscodeStep(build_dir),
    ]

    # Add steps specific to my machine or normie machine
    if is_normie:
        steps.append(
            FoldersStep(
                None,
                override_system_locations=False,
                separate_hw_tools=False,
                include_games=False,
                include_multimedia=False,
                include_projects=False,
                include_vms=False,
            )
        )
    else:
        steps += [
            FoldersStep(args.root_dir, include_multimedia=False),
            DushStep(fetch_git=True),
            GamesStep(),
            GitStep(),
            SshStep(secret_dir, args.full),
            ToolbarStep(root_dir),
            VirtualBoxStep(),
            MultimediaToolsStep(),
            ProgrammingCommonStep(),
            ProgrammingCppStep(False),
        ]

    return steps
