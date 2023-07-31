from .dwm.dwm import DwmStep  # TODO sort alphabetically
from .bluetooth.bluetooth import BluetoothStep
from .st.st import StStep
from .git import GitStep
from .virtualbox import VirtualBoxStep
from .firefox import FirefoxStep
from .packages import PackagesStep
from .bash_scripts import BashScriptsStep
from .vscode import VscodeStep
from .shell.shell import ShellStep
from .gtk_theme.gtk_theme import GtkThemeStep
from .file_associations import FileAssociationsStep
from .lightdm.lightdm import LightDmStep
from .thunar import ThunarStep
from .audio import AudioStep
from .java import JavaStep
from .gpu.gpu import GpuStep
from .home_directory.home_directory import HomeDirectoryStep
from .charon import CharonStep
from .picard import PicardStep
from .screen_config_persistance import ScreenConfigPersistanceStep
from .programming_cpp import ProgrammingCppStep
from .programming_rust import ProgrammingRustStep
from .programming_python import ProgrammingPythonStep
from .programming_common import ProgrammingCommonStep
from .programming_gamedev import ProgrammingGamedevStep
from .qbittorrent import QBitTorrentStep
from .raspberry_pi import RaspberryPiStep
from .encryption.encryption import EncryptionStep
from .notes import NotesStep
from .check_mate.check_mate import CheckMateStep
from .awesome.awesome import AwesomeStep
from .xsession import XsessionStep

from utils.setup_mode import SetupMode


def get_steps(args, root_dir, build_dir):
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
            CheckMateStep(build_dir),
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

    return steps
