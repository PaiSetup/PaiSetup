from .activate_windows import ActivateWindowsStep
from .explorer import ExplorerStep
from .extensions import ExtensionsStep
from .folders import FoldersStep
from .git import GitStep
from .hw_tools import HwToolsStep
from .packages.packages import PackagesStep
from .privacy import PrivacyStep
from .ssh import SshStep
from .uninstall_bloat import UninstallBloatStep
from .vscode import VscodeStep

from utils.setup_mode import SetupMode


def get_steps(args, root_dir, build_dir, secret_dir):
    steps = [
        # These steps should be at the beginning
        FoldersStep("D:/"),
        PackagesStep(build_dir, skip_already_installed=True),
        # For this steps order doesn't matter
        ActivateWindowsStep(secret_dir),
        ExplorerStep(),
        ExtensionsStep(),
        GitStep(),
        HwToolsStep(),
        PrivacyStep(),
        SshStep(secret_dir),
        UninstallBloatStep(),
        VscodeStep(build_dir),
    ]
    return steps
