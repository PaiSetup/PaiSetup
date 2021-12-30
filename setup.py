#!/usr/bin/env python3

from pathlib import Path
from utils.dependency_dispatcher import DependencyDispatcher
import sys

from steps.dwm.dwm import DwmStep
from steps.st.st import StStep
from steps.git import GitStep
from steps.packages import PackagesStep
from steps.dotfiles import DotFilesStep
from steps.bash_scripts import BashScriptsStep
from steps.vscode.vscode import VscodeStep
from steps.bash_prompt.bash_prompt import BashPromptStep
from steps.gtk_theme.gtk_theme import GtkThemeStep
from steps.file_associations import FileAssociationsStep
from steps.lightdm.lightdm import LightDmStep
from steps.audio import AudioStep
from steps.gpu import GpuStep


root_dir = Path(__file__).parent
build_dir = root_dir / "build"

# Setup steps. They can be safely commented out if neccessary
steps = [
    PackagesStep(build_dir, True),
    DotFilesStep(root_dir),
    BashScriptsStep(True, False),
    GitStep(),
    DwmStep(build_dir, True),
    StStep(build_dir, True),
    VscodeStep(build_dir),
    BashPromptStep(),
    GtkThemeStep(False),
    FileAssociationsStep(),
    LightDmStep(),
    AudioStep(),
    GpuStep(),
]

# Filter steps by command line args
if len(sys.argv) > 1:
    allowed_names = ["packages"] + [x.lower() for x in sys.argv[1:]]
    steps = [step for step in steps if step.name.lower() in allowed_names]

# Handle cross-step dependencies
dependencies = DependencyDispatcher()
for step in steps:
    step.register_as_dependency_listener(dependencies)
for step in steps:
    step.express_dependencies(dependencies)
dependencies.summary()


# Run the steps
for step in steps:
    step.perform()
