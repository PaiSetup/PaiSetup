from steps.ssh import SshStep
from utils.os_function import LinuxDistro
from utils.setup_mode import SetupMode

from .alacritty.alacritty import AlacrittyStep
from .audio import AudioStep
from .bluetooth.bluetooth import BluetoothStep
from .charon import CharonStep
from .claude import ClaudeStep
from .clion.clion import ClionStep
from .dush import DushStep
from .encryption.encryption import EncryptionStep
from .env import EnvStep
from .file_associations import FileAssociationsStep
from .firefox import FirefoxStep
from .flameshot import FlameshotStep
from .git import GitStep
from .gpu.gpu import GpuStep
from .gtk_theme.gtk_theme import GtkThemeStep
from .gui.awesome.awesome import AwesomeStep
from .gui.gui_xorg import GuiXorg
from .gui.qtile.qtile import QtileStep
from .guild_wars2 import GuildWars2Step
from .home_directory.home_directory import HomeDirectoryStep
from .icon_font.icon_font import FontStep
from .lightdm.lightdm import LightDmStep
from .multimedia_software_step import MultimediaSoftwareStep
from .neovim.neovim import NeovimStep
from .notes.notes import NotesStep
from .nush import NushStep
from .packages import PackagesStep
from .packages_debian.packages_debian import PackagesDebianStep
from .plex.plex import PlexStep
from .programming_common import ProgrammingCommonStep
from .programming_cpp import ProgrammingCppStep
from .programming_gamedev import ProgrammingGamedevStep
from .programming_go import ProgrammingGoStep
from .programming_java import ProgrammingJavaStep
from .programming_node import ProgrammingNodeStep
from .programming_python import ProgrammingPythonStep
from .programming_rust import ProgrammingRustStep
from .qbittorrent import QBitTorrentStep
from .raspberry_pi import RaspberryPiStep
from .rpi_led.rpi_led import RpiLedStep
from .shell.shell import ShellStep
from .spieven.spieven import SpievenStep
from .systemd import SystemdStep
from .thunar import ThunarStep
from .udiskie_step import UdiskieStep
from .ulauncher import UlauncherStep
from .useless import UselessStep
from .vagrant import VagrantStep
from .virtualbox import VirtualBoxStep
from .vscode import VscodeStep


class ArchSetupMode(SetupMode):
    def get_name(self):
        return "arch"

    def is_compatible(self):
        return LinuxDistro.current().is_arch_like()

    def get_steps(self):
        return [
            PackagesStep(),
            EnvStep(),
            ShellStep(),
            GtkThemeStep(),
            FileAssociationsStep(),
            AudioStep(),
            ClionStep(),
            UdiskieStep(),
            GpuStep(),
            FirefoxStep(is_default_browser=True),
            FlameshotStep(),
            SystemdStep(),
            ThunarStep(),
            HomeDirectoryStep(True),
            BluetoothStep(),
            ProgrammingJavaStep(include_android=True),
            QBitTorrentStep(),
            GitStep(),
            UlauncherStep(),
            GuiXorg(),
            AwesomeStep(),
            AlacrittyStep(),
            MultimediaSoftwareStep(),
            DushStep(),
            NushStep(),
            VscodeStep(),
            NeovimStep(),
            RpiLedStep(),
            UselessStep(),
            GuildWars2Step(),
            FontStep(),
            PlexStep(),
            ProgrammingCppStep(graphics=True, systemc=True),
            ProgrammingPythonStep(),
            ProgrammingRustStep(),
            ProgrammingCommonStep(),
            ProgrammingGamedevStep(),
            ProgrammingGoStep(),
            ProgrammingNodeStep(),
            ClaudeStep(),
            SshStep(),
            SpievenStep(),
            LightDmStep(),
            EncryptionStep(),
            CharonStep(),
            QtileStep(),
            NotesStep(use_private_notes=True),
            VirtualBoxStep(),
            VagrantStep(),
            RaspberryPiStep(),
        ]


class DebianCasualSetupMode(SetupMode):
    def get_name(self):
        return "debian_casual"

    def is_compatible(self):
        return LinuxDistro.current().is_debian_like()

    def get_steps(self):
        return [
            PackagesDebianStep(),
            EnvStep(),
            AwesomeStep(),
            ProgrammingCommonStep(),
            ProgrammingPythonStep(),
            GitStep(),
            UdiskieStep(),
            AudioStep(),
            ThunarStep(),
            SpievenStep(),
            ShellStep(),
            MultimediaSoftwareStep(),
            QBitTorrentStep(),
            GuiXorg(),
            FontStep(),
            AlacrittyStep(),
            GtkThemeStep(),
            FirefoxStep(is_default_browser=True),
            FileAssociationsStep(),
            HomeDirectoryStep(has_multimedia_dir=False),
            UlauncherStep(),
            DushStep(),
            NushStep(),
            SshStep(),
            VscodeStep(),
        ]


SETUP_MODES = [ArchSetupMode, DebianCasualSetupMode]
