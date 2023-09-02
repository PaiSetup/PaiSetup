from .activate_windows import ActivateWindowsStep
from .explorer import ExplorerStep
from .extensions import ExtensionsStep
from .folders import FoldersStep
from .games import GamesStep
from .git import GitStep
from .hw_tools import HwToolsStep
from .multimedia_tools import MultimediaToolsStep
from .icons.icons import IconsStep
from .packages.packages import PackagesStep
from .power import PowerStep
from .privacy import PrivacyStep
from .programming_common import ProgrammingCommonStep
from .programming_cpp import ProgrammingCppStep
from .ssh import SshStep
from .startup import StartupStep
from .time import TimeStep
from .toolbar import ToolbarStep
from .uninstall_bloat import UninstallBloatStep
from .virtualbox import VirtualBoxStep
from .vscode import VscodeStep

from utils.setup_mode import SetupMode


def get_steps(args, root_dir, build_dir, secret_dir):
    # TODO check for admin

    steps = []

    # Add packages step. It should be before all other steps. TODO: resolve execution dependencies automatically.
    steps.append(PackagesStep(build_dir, skip_already_installed=True, is_main_machine=args.mode == SetupMode.main))

    # Add folder step
    if args.mode == SetupMode.main:
        steps.append(FoldersStep(args.root_dir, include_multimedia=False))
    elif args.mode == SetupMode.normie:
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
    elif args.mode == SetupMode.extra:
        steps.append(FoldersStep(args.root_dir, include_multimedia=False, include_projects=False, include_vms=False))
    else:
        raise ValueError("Unsupported mode")

    # Add the rest of the steps
    steps += [
        ActivateWindowsStep(secret_dir),
        ExplorerStep(),
        ExtensionsStep(),
        GitStep(),
        HwToolsStep(gaming=args.mode == SetupMode.main),
        IconsStep(),
        PowerStep(),
        PrivacyStep(),
        SshStep(secret_dir),
        TimeStep(),
        StartupStep(),
        UninstallBloatStep(),
        VscodeStep(build_dir),
    ]

    # Add steps only for my machines
    if args.mode == SetupMode.main or args.mode == SetupMode.extra:
        steps += [
            GamesStep(),
            ToolbarStep(root_dir),
            VirtualBoxStep(),
        ]

    # Add steps only for main machine
    if args.mode == SetupMode.main:
        steps += [
            MultimediaToolsStep(),
            ProgrammingCommonStep(),
            ProgrammingCppStep(False),
        ]

    return steps
