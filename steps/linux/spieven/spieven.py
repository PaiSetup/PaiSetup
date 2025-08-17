from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path

import utils.external_project as ext
from steps.step import Step
from utils.command import *
from utils.dependency_dispatcher import push_dependency_handler
from utils.services.file_writer import FileType


class SpievenDisplayType(Enum):
    Headless = auto()
    Xorg = auto()
    Wayland = auto()


class SpievenTaskType(Enum):
    Daemon = auto()
    PeriodicCheck = auto()
    PeriodicAction = auto()


@dataclass
class SpievenTask:
    name: str
    cmdline: str
    task_type: SpievenTaskType
    display_type: SpievenDisplayType
    delay: int


class SpievenStep(Step):
    def __init__(self, root_build_dir):
        super().__init__("Spieven")
        self._root_build_dir = root_build_dir
        self._current_step_dir = Path(__file__).parent

        self._tasks = []

        # fmt: off
        self.schedule_spieven_periodic_action("KeyboardLayout",     self._current_step_dir / "check_keyboard_layout.sh",     display_type=SpievenDisplayType.Xorg,     delay_ms=60_000)
        self.schedule_spieven_periodic_check("NetworkConnected",    self._current_step_dir / "check_network_connected.sh",   display_type=SpievenDisplayType.Headless, delay_ms=10_000)
        self.schedule_spieven_periodic_check("NetworkInterface",    self._current_step_dir / "check_network_interface.sh",   display_type=SpievenDisplayType.Headless, delay_ms=10_000)
        self.schedule_spieven_periodic_check("ScriptsWarnings",     self._current_step_dir / "check_scripts_warnings.sh",    display_type=SpievenDisplayType.Headless, delay_ms=15_000)
        self.schedule_spieven_periodic_check("Trash",               self._current_step_dir / "check_trash.sh",               display_type=SpievenDisplayType.Headless, delay_ms=60_000)
        self.schedule_spieven_periodic_check("UnmatchingPackages",  self._current_step_dir / "check_unmatching_packages.sh", display_type=SpievenDisplayType.Headless, delay_ms=20_000)
        self.schedule_spieven_periodic_check("UpdatedKernel",       self._current_step_dir / "check_updated_kernel.sh",      display_type=SpievenDisplayType.Headless, delay_ms=60_000)
        # fmt: on

    @push_dependency_handler
    def schedule_spieven_task(self, task_type, name, cmdline, display_type, delay_ms):
        task = SpievenTask(
            name=name,
            cmdline=cmdline,
            task_type=task_type,
            display_type=display_type,
            delay=delay_ms,
        )
        self._tasks.append(task)

    @push_dependency_handler
    def schedule_spieven_daemon(self, name, cmdline, display_type):
        self.schedule_spieven_task(SpievenTaskType.Daemon, name, cmdline, display_type, 1_000)

    @push_dependency_handler
    def schedule_spieven_periodic_check(self, name, cmdline, display_type, delay_ms):
        self.schedule_spieven_task(SpievenTaskType.PeriodicCheck, name, cmdline, display_type, delay_ms)

    @push_dependency_handler
    def schedule_spieven_periodic_action(self, name, cmdline, display_type, delay_ms):
        self.schedule_spieven_task(SpievenTaskType.PeriodicAction, name, cmdline, display_type, delay_ms)

    def perform(self):
        self._install()
        self._setup_launch_script()

    def _install(self):
        spieven_version = "1.0.1"
        dst_dir = self._root_build_dir / f"spieven-{spieven_version}"
        ext.download_github_release(
            "DziubanMaciej",
            "Spieven",
            dst_dir,
            spieven_version,
            f"spieven-{spieven_version}.zip",
            re_download=False,
        )
        self._file_writer.write_symlink_executable(dst_dir / "spieven", "spieven")

    def _setup_launch_script(self):
        commands = []
        task_names = []

        for task in self._tasks:
            task_delay_str = str(task.delay).rjust(5)
            name_arg = f"-n {task.name.ljust(18)}"

            match task.display_type:
                case SpievenDisplayType.Headless:
                    display_arg = "-p h"
                case SpievenDisplayType.Xorg:
                    display_arg = "-p x"
                case SpievenDisplayType.Wayland:
                    display_arg = "-p w"
                case _:
                    raise ValueError("Invalid DisplayType")

            match task.task_type:
                case SpievenTaskType.Daemon:
                    max_failures_arg = "-m  3"
                    delay_arg = f"-s     0 -f {task_delay_str}"
                    tags_arg = "-t PaiSetup,PaiSetupDaemon       "
                    capture_stdout_arg = "  "
                case SpievenTaskType.PeriodicCheck:
                    max_failures_arg = "-m -1"
                    delay_arg = f"-s {task_delay_str} -f {task_delay_str}"
                    tags_arg = "-t PaiSetup,PaiSetupPeriodicCheck"
                    capture_stdout_arg = "-c"
                case SpievenTaskType.PeriodicAction:
                    max_failures_arg = "-m -1"
                    delay_arg = f"-s {task_delay_str} -f {task_delay_str}"
                    tags_arg = "-t PaiSetup,PaiSetupPeriodicAction"
                    capture_stdout_arg = "  "
                case _:
                    raise ValueError("Invalid DisplayType")

            command = f"spieven schedule {name_arg} {display_arg} {max_failures_arg} {delay_arg} {tags_arg} {capture_stdout_arg} -- {task.cmdline}"
            commands.append(command)
            task_names.append(task.name)

        env_line = f"export PAI_SETUP_SPIEVEN_TASKS=" + ",".join(task_names)
        lines = commands + [env_line]
        self._file_writer.write_lines(
            ".config/PaiSetup/run_spieven.sh",
            lines,
        )
        self._file_writer.write_section(
            ".config/PaiSetup/xinitrc_base",
            "Schedule background tasks",
            [". ~/.config/PaiSetup/run_spieven.sh"],
        )
