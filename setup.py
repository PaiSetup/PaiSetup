#!/usr/bin/env python3

import argparse
from pathlib import Path

from steps import get_steps
from steps.step import Step
from utils.argparser_utils import EnumAction, PathAction
from utils.dependency_dispatcher import DependencyDispatcher
from utils.os_function import OperatingSystem
from utils.setup_mode import SetupMode

# Prepare common paths
root_dir = Path(__file__).parent
build_dir = root_dir / "build"
secret_dir = root_dir / "secret"
logs_dir = root_dir / "logs"

# Parse command-line arguments
# fmt: off
arg_parser = argparse.ArgumentParser(description="Setup Arch Linux environment.", allow_abbrev=False)
arg_parser.add_argument("-l", "--list_steps", action="store_true", help="show setup steps to be run and exit")
arg_parser.add_argument("-p", "--list_packages", action="store_true", help="show packages to be installed and exit")
arg_parser.add_argument("-m", "--mode", type=SetupMode, default=SetupMode.retrieve_last_mode(root_dir), action=EnumAction, help="Setup mode - chooses packages to install")
arg_parser.add_argument("-s", "--steps", nargs="+", metavar="STEP", help="filter steps to perform during setup for a given mode")
arg_parser.add_argument("-f", "--full", action="store_true", help="Do not skip any operation for performance. Generate everything from scratch.")
arg_parser.add_argument("-a", "--no_auto_resolve_dependencies", action="store_true", help="Do not automatically enable disabled steps if they are depended on by other enabled steps. This can lead to errors.")
if OperatingSystem.current().is_windows():
    arg_parser.add_argument("-r", "--root_dir", action=PathAction, default="D:\\", help="Main directory for user workspace.")
args = arg_parser.parse_args()
args.mode.save_last_mode(root_dir)
# fmt: on

# Setup services
disable_logger = args.list_steps or args.list_packages
Step.setup_external_services(root_dir, logs_dir, disable_logger)

# Setup steps. They can be safely commented out if neccessary
Step._logger.log("Initializing steps")
steps = get_steps(args, root_dir, build_dir, secret_dir)

# Filter steps by command line args
Step._logger.log("Filtering steps")
if args.steps != None:
    allowed_names = [x.lower() for x in args.steps]
    for step in steps:
        if step.name.lower() not in allowed_names:
            step.set_enabled(False)

# Setup env
Step._logger.log("Setting up environment variables")
for step in steps:
    step.register_env_variables()

# Handle cross-step dependencies
Step._logger.log("Handling steps dependencies")
dependencies = DependencyDispatcher(not args.no_auto_resolve_dependencies)
for step in steps:
    dependencies.register_handlers(step)
enabled_steps = [step for step in steps if step.is_enabled()]  # Save into variable, because steps may be enabled during iteration
for step in enabled_steps:
    step.express_dependencies(dependencies)

# List steps
if args.list_steps:
    for step in steps:
        if step.is_enabled():
            print(step.name)
    exit(0)

# List packages
if args.list_packages:
    dependencies.list_packages(True)
    exit(0)

# Run the steps
with Step._logger.indent("Executing steps"):
    for step in steps:
        if step.is_enabled() and step.is_method_overriden(Step.perform):
            Step._logger.log(f"Performing step: {step.name}", short_message=f"{step.name}Step")
            with Step._logger.indent():
                step.perform()

# Finalize services
Step.finalize_services()
