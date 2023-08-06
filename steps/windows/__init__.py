from .activate_windows import ActivateWindowsStep
from .explorer import ExplorerStep
from .folders import FoldersStep
from .git import GitStep
from .hw_tools import HwToolsStep
from .packages.packages import PackagesStep
from .vscode import VscodeStep

from utils.setup_mode import SetupMode


def get_steps(args, root_dir, build_dir):
    steps = [
        FoldersStep("D:/"),
        PackagesStep(build_dir, skip_already_installed=True),

        ActivateWindowsStep(root_dir),
        ExplorerStep(),
        GitStep(),
        VscodeStep(build_dir),
        HwToolsStep(),
    ]
    return steps
