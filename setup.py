#!/usr/bin/env python3

import argparse
from pathlib import Path

from steps import get_steps
from steps.step import Step
from utils.argparser_utils import EnumAction, PathAction
from utils.dependency_dispatcher import DependencyResolutionMode
from utils.execute_steps import execute_steps
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
arg_parser.add_argument("-d", "--dependency_resolution_mode", type=DependencyResolutionMode, default=DependencyResolutionMode.pull_and_push, action=EnumAction, help="Decide which dependency types are used for implicit dependency resolution.")
if OperatingSystem.current().is_windows():
    arg_parser.add_argument("-r", "--root_dir", action=PathAction, default="D:\\", help="Main directory for user workspace.")
args = arg_parser.parse_args()
args.mode.save_last_mode(root_dir)
# fmt: on

# Setup services.
enable_perf_analyzer = True
enable_logger = not (args.list_steps or args.list_packages)
Step.setup_external_services(root_dir, logs_dir, enable_perf_analyzer, enable_logger)

# Setup steps.
Step._logger.log("Initializing steps")
steps = get_steps(args, root_dir, build_dir, secret_dir)

execute_steps(steps, args.steps, args.dependency_resolution_mode, args.list_steps, args.list_packages)
