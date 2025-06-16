#!/usr/bin/env python3

import argparse
from pathlib import Path

from steps import get_steps
from steps.step import Step
from utils.argparser_utils import EnumAction, PathAction
from utils.dependency_dispatcher import DependencyResolutionMode
from utils.execute_steps import execute_steps
from utils.os_function import OperatingSystem
from utils.services.services import Services
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
arg_parser.add_argument("-s", "--step_whitelist", nargs="+", metavar="STEP", help="Limit executed steps by names. Note that other steps may be implicitly enabled due to dependencies. Mutually exclusive with --step-blacklist.")
arg_parser.add_argument("-e", "--step_blacklist", nargs="+", metavar="STEP", help="Exclude steps from execution. Note that other steps may be implicitly enabled due to dependencies. Mutually exclusive with --step-whitelist.")
arg_parser.add_argument("-f", "--full", action="store_true", help="Do not skip any operation for performance. Generate everything from scratch.")
arg_parser.add_argument("-k", "--skip_packages", action="store_true", help="Skip package installation.")
arg_parser.add_argument("-a", "--pause", action="store_true", help="Enable pause mode. Execution will stop and wait for user input before every Step.perform(). Press Enter to proceed.")
arg_parser.add_argument("-d", "--dependency_resolution_mode", type=DependencyResolutionMode, default=DependencyResolutionMode.pull_and_push, action=EnumAction, help="Decide which dependency types are used for implicit dependency resolution.")
arg_parser.add_argument("-u", "--allow_unsatisfied_push_dependencies", action="store_true", help="Only print warnings when there are not matching handlers for a push dependency. This should be used only for debug purposes")
if OperatingSystem.current().is_windows():
    arg_parser.add_argument("-r", "--root_dir", action=PathAction, default="D:\\", help="Main directory for user workspace.")
args = arg_parser.parse_args()
args.mode.save_last_mode(root_dir)
# fmt: on

enable_perf_analyzer = True
enable_logger = not (args.list_steps or args.list_packages)
with Services(root_dir, logs_dir, enable_perf_analyzer, enable_logger) as services:
    services.assign_to(Step)

    Step._logger.log("Initializing steps")
    steps = get_steps(args, root_dir, build_dir, secret_dir, not args.skip_packages)

    execute_steps(
        services,
        steps,
        args.step_whitelist,
        args.step_blacklist,
        args.dependency_resolution_mode,
        args.allow_unsatisfied_push_dependencies,
        args.list_steps,
        args.list_packages,
        args.pause,
    )
