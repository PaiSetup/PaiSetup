#!/usr/bin/env python3

from steps.step import Step
from steps.linux import get_steps
from utils.dependency_dispatcher import DependencyDispatcher
from utils.env import EnvManager
from utils.file_writer import FileWriter
from utils.setup_mode import SetupMode

from pathlib import Path
from utils.argparser_utils import EnumAction
from utils.log import log, LogIndent
import argparse

# Prepare common paths
root_dir = Path(__file__).parent
build_dir = root_dir / "build"

# Parse command-line arguments
# fmt: off
arg_parser = argparse.ArgumentParser(description="Setup Arch Linux environment.", allow_abbrev=False)
arg_parser.add_argument("-l", "--list_steps", action="store_true", help="show setup steps to be run and exit")
arg_parser.add_argument("-p", "--list_packages", action="store_true", help="show packages to be installed and exit")
arg_parser.add_argument("-m", "--mode", type=SetupMode, default=SetupMode.retrieve_last_mode(root_dir), action=EnumAction, help="Setup mode - chooses packages to install")
arg_parser.add_argument("-s", "--steps", nargs="+", metavar="STEP", help="filter steps to perform during setup for a given mode")
arg_parser.add_argument("-f", "--fetch", action="store_true", help="fetch git repositories which might have changed. Some repositories is still not fetched, e.g. dwm, which does not change very often")
args = arg_parser.parse_args()
args.mode.save_last_mode(root_dir)
# fmt: on

# Setup services
file_writer = FileWriter()
env = EnvManager(root_dir)
Step.setup_external_services(file_writer, env)

# Setup steps. They can be safely commented out if neccessary

steps = get_steps(args, root_dir, build_dir)

# Filter steps by command line args
if args.steps != None:
    allowed_names = ["packages"] + [x.lower() for x in args.steps]
    steps = [step for step in steps if step.name.lower() in allowed_names]

# List steps
if args.list_steps:
    for step in steps:
        print(step.name)
    exit(0)

# Setup env
for step in steps:
    step.register_env_variables()

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
    if step.is_method_overriden(Step.perform):
        log(f"Performing step: {step.name}")
        with LogIndent():
            step.perform()

# Finalize services
file_writer.finalize()
