from .vscode import VscodeStep

from utils.setup_mode import SetupMode


def get_steps(args, root_dir, build_dir):
    steps = [
        VscodeStep(build_dir),
    ]
    return steps
