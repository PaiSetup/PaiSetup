#!/usr/bin/env python3

import argparse
from pathlib import Path

from steps.step import Step
from utils.argparser_utils import EnumAction, PathAction, SetupModeAction
from utils.dependency_dispatcher import DependencyResolutionMode
from utils.execute_steps import execute_steps
from utils.os_function import OperatingSystem
from utils.services.setup_flags import SetupFlags
from utils.services.services import Services
from utils.setup_mode import SetupMode

# Prepare common paths
pai_setup_dir = Path(__file__).parent

# Gather all available setup modes
setup_modes = SetupMode.find_setup_modes()

# Parse command-line arguments
# fmt: off
arg_parser = argparse.ArgumentParser(description="Setup Arch Linux environment.", allow_abbrev=False)
arg_parser.add_argument("-l", "--list_steps", action="store_true", help="show setup steps to be run and exit")
arg_parser.add_argument("-p", "--list_packages", action="store_true", help="show packages to be installed and exit")
arg_parser.add_argument("-m", "--mode", default=SetupMode.retrieve_last_mode(pai_setup_dir, setup_modes), action=SetupModeAction, setup_modes=setup_modes, help="Setup mode - chooses packages to install")
arg_parser.add_argument("-s", "--step_whitelist", nargs="+", metavar="STEP", help="Limit executed steps by names. Note that other steps may be implicitly enabled due to dependencies. Mutually exclusive with --step-blacklist.")
arg_parser.add_argument("-e", "--step_blacklist", nargs="+", metavar="STEP", help="Exclude steps from execution. Note that other steps may be implicitly enabled due to dependencies. Mutually exclusive with --step-whitelist.")
arg_parser.add_argument("--strict_download", action="store_true", help="Fetch git repositories and download files even if they are already present. Content that is both downloaded and built is also rebuilt.")
arg_parser.add_argument("--strict_build", action="store_true", help="Build binaries and generate content even if it is already present.")
arg_parser.add_argument("--strict_install", action="store_true", help="Install packages even if they are already installed.")
arg_parser.add_argument("--strict_explorer", action="store_true", help="Restart Windows Explorer, so that its settings take effect immediately.")
arg_parser.add_argument("-f", "--strict_full", action="store_true", help="Enable all --strict_* options. The run is slower, but does not skip any work it believes is already done.")
arg_parser.add_argument("-k", "--skip_packages", action="store_true", help="Skip package installation.")
arg_parser.add_argument("-a", "--pause", action="store_true", help="Enable pause mode. Execution will stop and wait for user input before every Step.perform(). Press Enter to proceed.")
arg_parser.add_argument("-d", "--dependency_resolution_mode", type=DependencyResolutionMode, default=DependencyResolutionMode.pull_and_push, action=EnumAction, help="Decide which dependency types are used for implicit dependency resolution.")
arg_parser.add_argument("-u", "--allow_unsatisfied_push_dependencies", action="store_true", help="Only print warnings when there are not matching handlers for a push dependency. This should be used only for debug purposes")
args = arg_parser.parse_args()
args.mode.save_last_mode(pai_setup_dir)
# fmt: on

flags = SetupFlags(
    install_packages=not args.skip_packages,
    strict_download=args.strict_download or args.strict_full,
    strict_build=args.strict_build or args.strict_full,
    strict_install=args.strict_install or args.strict_full,
    strict_explorer=args.strict_explorer or args.strict_full,
)

enable_logger = not (args.list_steps or args.list_packages)
enable_perf_analyzer = not (args.list_steps or args.list_packages)
with Services(pai_setup_dir, flags, enable_perf_analyzer, enable_logger) as services:
    services.assign_to(Step)

    Step._logger.log("Initializing steps")
    steps = args.mode.get_steps()

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
