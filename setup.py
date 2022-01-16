#!/usr/bin/env python3

from pathlib import Path
from utils.dependency_dispatcher import DependencyDispatcher
import argparse
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
from steps.charon import CharonStep


# Parse command-line arguments
arg_parser = argparse.ArgumentParser(description="Setup Arch Linux environment.", allow_abbrev=False)
arg_parser.add_argument("--normie", action="store_true", help="Use only normie steps")
arg_parser.add_argument("-s", "--steps", nargs="+", help="steps")
arg_parser.add_argument("-l", "--list_steps", action="store_true", help="Print steps to be run and exit")
arg_parser.add_argument("-p", "--list_packages", action="store_true", help="Print packages to be installed and exit")
args = arg_parser.parse_args()


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
if args.normie:
    # TODO: setup kde or something like that
    pass
else:
    steps += [
        DwmStep(build_dir, fetch_git=False),
        StStep(build_dir, fetch_git=True),
        LightDmStep(),
        BashScriptsStep(fetch_git=True),
        GitStep(),
        VscodeStep(build_dir),
        CharonStep(build_dir, fetch_git=False),
    ]

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
