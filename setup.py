#!/usr/bin/env python3

from pathlib import Path
from utils.argparser_utils import EnumAction
from utils.log import log, LogIndent
import argparse
import sys
import enum

from utils.dependency_dispatcher import DependencyDispatcher
from utils.file_writer import FileWriter
from utils.env import EnvManager

from steps.step import Step
from steps.dwm.dwm import DwmStep
from steps.bluetooth.bluetooth import BluetoothStep
from steps.st.st import StStep
from steps.git import GitStep
from steps.virtualbox import VirtualBoxStep
from steps.firefox import FirefoxStep
from steps.packages import PackagesStep
from steps.bash_scripts import BashScriptsStep
from steps.vscode.vscode import VscodeStep
from steps.shell.shell import ShellStep
from steps.gtk_theme.gtk_theme import GtkThemeStep
from steps.file_associations import FileAssociationsStep
from steps.lightdm.lightdm import LightDmStep
from steps.thunar import ThunarStep
from steps.audio import AudioStep
from steps.java import JavaStep
from steps.gpu.gpu import GpuStep
from steps.home_directory.home_directory import HomeDirectoryStep
from steps.charon import CharonStep
from steps.picard import PicardStep
from steps.screen_config_persistance import ScreenConfigPersistanceStep
from steps.programming_cpp import ProgrammingCppStep
from steps.programming_rust import ProgrammingRustStep
from steps.programming_python import ProgrammingPythonStep
from steps.programming_common import ProgrammingCommonStep
from steps.programming_gamedev import ProgrammingGamedevStep
from steps.qbittorrent import QBitTorrentStep
from steps.raspberry_pi import RaspberryPiStep
from steps.encryption.encryption import EncryptionStep
from steps.notes import NotesStep
from steps.bg_checker.bg_checker import BgChckerStep
from steps.awesome.awesome import AwesomeStep
from steps.xsession import XsessionStep


class SetupMode(enum.Enum):
    main = "main"  # My main machine
    normie = "normie"  # Setup for beginners
    normie_plus = "normie_plus"  # Setup for beginners + additional stuff like tiling WMs, so I can comfortably use it as well


# Retrieve last mode
lastmode_file = Path(__file__).parent / ".lastmode"
try:
    with open(lastmode_file, "r") as file:
        lastmode = SetupMode(file.readline().strip())
except (FileNotFoundError, ValueError) as e:
    lastmode = SetupMode.main


# Parse command-line arguments
# fmt: off
arg_parser = argparse.ArgumentParser(description="Setup Arch Linux environment.", allow_abbrev=False)
arg_parser.add_argument("-l", "--list_steps", action="store_true", help="show setup steps to be run and exit")
arg_parser.add_argument("-p", "--list_packages", action="store_true", help="show packages to be installed and exit")
arg_parser.add_argument("-m", "--mode", type=SetupMode, default=lastmode, action=EnumAction, help="Setup mode - chooses packages to install")
arg_parser.add_argument("-s", "--steps", nargs="+", metavar="STEP", help="filter steps to perform during setup for a given mode")
arg_parser.add_argument("-f", "--fetch", action="store_true", help="fetch git repositories which might have changed. Some repositories is still not fetched, e.g. dwm, which does not change very often")
args = arg_parser.parse_args()
# fmt: on

# Save last mode to a file
with open(lastmode_file, "w") as file:
    file.write(f"{args.mode.value}\n")

# Setup services
root_dir = Path(__file__).parent
file_writer = FileWriter()
env = EnvManager(root_dir)
Step.setup_external_services(file_writer, env)

# Setup steps. They can be safely commented out if neccessary
build_dir = root_dir / "build"
steps = [
    PackagesStep(build_dir, True),
    ShellStep(root_dir),
    GtkThemeStep(regenerate_widget_theme=False, regenerate_icon_theme=False),
    FileAssociationsStep(),
    AudioStep(),
    ScreenConfigPersistanceStep(),
    GpuStep(),
    FirefoxStep(is_default_browser=True),
    ThunarStep(is_main_machine=args.mode == SetupMode.main),
    HomeDirectoryStep(is_main_machine=args.mode == SetupMode.main),
    BluetoothStep(),
    JavaStep(),
    QBitTorrentStep(is_main_machine=args.mode == SetupMode.main),
]
if args.mode == SetupMode.main or args.mode == SetupMode.normie_plus:
    steps += [
        XsessionStep(),
        GitStep(),
        DwmStep(build_dir, fetch_git=False, is_default_wm=False),
        AwesomeStep(build_dir, fetch_git=False, is_default_wm=True),
        StStep(build_dir, fetch_git=False),
        BashScriptsStep(fetch_git=args.fetch),
        VscodeStep(build_dir),
        ProgrammingCppStep(graphics=True, systemc=True),
        ProgrammingPythonStep(),
        ProgrammingRustStep(),
        ProgrammingCommonStep(),
        ProgrammingGamedevStep(),
        BgChckerStep(build_dir),
    ]
if args.mode == SetupMode.main:
    steps += [
        LightDmStep(),
        EncryptionStep(),
        CharonStep(build_dir, fetch_git=args.fetch),
        PicardStep(),
        NotesStep(fetch_git=args.fetch),
        VirtualBoxStep(),
        RaspberryPiStep(),
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
