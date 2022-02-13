#!/usr/bin/env python3

from pathlib import Path
from utils.dependency_dispatcher import DependencyDispatcher
from utils.argparser_utils import EnumAction
import argparse
import sys
import enum

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
from steps.charon import CharonStep


class SetupMode(enum.Enum):
    main = 1  # My main machine
    normie = 2  # Setup for beginners
    normie_plus = 3  # Setup for beginners + additional stuff like DWM, so I can comfortably use it as well


# Parse command-line arguments
# fmt: off
arg_parser = argparse.ArgumentParser(description="Setup Arch Linux environment.", allow_abbrev=False)
arg_parser.add_argument("-l", "--list_steps", action="store_true", help="show setup steps to be run and exit")
arg_parser.add_argument("-p", "--list_packages", action="store_true", help="show packages to be installed and exit")
arg_parser.add_argument("-m", "--mode", type=SetupMode, default=SetupMode.main, action=EnumAction, help="Setup mode - chooses packages to install")
arg_parser.add_argument("-s", "--steps", nargs="+", metavar="STEP", help="filter steps to perform during setup for a given mode")
args = arg_parser.parse_args()
# fmt: on


# Setup steps. They can be safely commented out if neccessary
root_dir = Path(__file__).parent
build_dir = root_dir / "build"
steps = [
    PackagesStep(build_dir, True),
    DotFilesStep(root_dir),
    BashPromptStep(),
    GtkThemeStep(False),
    FileAssociationsStep(),
    AudioStep(),
    GpuStep(),
]
if args.mode == SetupMode.main or args.mode == SetupMode.normie_plus:
    steps += [
        DwmStep(build_dir, fetch_git=False),
        StStep(build_dir, fetch_git=True),
        BashScriptsStep(fetch_git=True),
        GitStep(),
        VscodeStep(build_dir),
    ]
if args.mode == SetupMode.main:
    steps += [
        LightDmStep(),
        CharonStep(build_dir, fetch_git=False),
    ]
if args.mode == SetupMode.normie:
    # TODO: setup kde or something like that
    pass


# Filter steps by command line args
if args.steps != None:
    allowed_names = ["packages"] + [x.lower() for x in args.steps]
    steps = [step for step in steps if step.name.lower() in allowed_names]

# List steps
if args.list_steps:
    for step in steps:
        print(step.name)
    exit(0)

# Handle cross-step dependencies
dependencies = DependencyDispatcher()
for step in steps:
    step.register_as_dependency_listener(dependencies)
for step in steps:
    step.express_dependencies(dependencies)
dependencies.summary()

# List packages
if args.list_packages:
    dependencies.list_packages(True)
    exit(0)

# Run the steps
for step in steps:
    step.perform()
