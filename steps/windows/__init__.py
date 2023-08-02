from .packages.packages import PackagesStep
from .hw_tools import HwToolsStep
from .vscode import VscodeStep

from utils.setup_mode import SetupMode


def get_steps(args, root_dir, build_dir):
    steps = [
        PackagesStep(build_dir, skip_already_installed=False),
        VscodeStep(build_dir),
        HwToolsStep(),
    ]
    return steps
