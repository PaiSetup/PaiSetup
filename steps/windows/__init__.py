from .explorer import ExplorerStep
from .folders import FoldersStep
from .hw_tools import HwToolsStep
from .packages.packages import PackagesStep
from .vscode import VscodeStep

from utils.setup_mode import SetupMode


def get_steps(args, root_dir, build_dir):
    steps = [
        ExplorerStep(),
        FoldersStep("D:/"),
        PackagesStep(build_dir, skip_already_installed=True),
        VscodeStep(build_dir),
        HwToolsStep(),
    ]
    return steps
