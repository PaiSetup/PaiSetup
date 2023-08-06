from .activate_windows import ActivateWindowsStep
from .explorer import ExplorerStep
from .folders import FoldersStep
from .git import GitStep
from .hw_tools import HwToolsStep
from .packages.packages import PackagesStep
from .ssh import SshStep
from .vscode import VscodeStep

from utils.setup_mode import SetupMode


def get_steps(args, root_dir, build_dir, secret_dir):
    steps = [
        FoldersStep("D:/"),
        PackagesStep(build_dir, skip_already_installed=True),

        ActivateWindowsStep(secret_dir),
        ExplorerStep(),
        GitStep(),
        HwToolsStep(),
        SshStep(secret_dir),
        VscodeStep(build_dir),
    ]
    return steps
