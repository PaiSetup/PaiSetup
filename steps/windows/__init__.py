from .activate_windows import ActivateWindowsStep
from .explorer import ExplorerStep
from .extensions import ExtensionsStep
from .folders import FoldersStep
from .git import GitStep
from .hw_tools import HwToolsStep
from .icons.icons import IconsStep
from .packages.packages import PackagesStep
from .power import PowerStep
from .privacy import PrivacyStep
from .ssh import SshStep
from .startup import StartupStep
from .time import TimeStep
from .uninstall_bloat import UninstallBloatStep
from .vscode import VscodeStep

from utils.setup_mode import SetupMode


def get_steps(args, root_dir, build_dir, secret_dir):
    steps = []

    # Add folder step
    if args.mode == SetupMode.main:
        steps.append(FoldersStep("D:/", include_multimedia=False))
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
        steps.append(FoldersStep("D:/", include_multimedia=False, include_projects=False, include_vms=False))
    else:
        raise ValueError("Unsupported mode")

    # Add packages step. It should be before all other steps. TODO: resolve execution dependencies automatically.
    steps.append(PackagesStep(build_dir, skip_already_installed=True))

    # Add the rest of the steps
    steps += [
        ActivateWindowsStep(secret_dir),
        ExplorerStep(),
        ExtensionsStep(),
        GitStep(),
        HwToolsStep(),
        IconsStep(),
        PowerStep(),
        PrivacyStep(),
        SshStep(secret_dir),
        TimeStep(),
        StartupStep(),
        UninstallBloatStep(),
        VscodeStep(build_dir),
    ]
    return steps
