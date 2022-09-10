from steps.step import Step
import os
import utils.external_project as ext
from utils.log import log, LogIndent
from utils import command
from pathlib import Path
from utils.file_writer import FileType, FileWriter


class BgChckerStep(Step):
    """
    BgChecker is a C++ client/server application written for the purposes of LinuxSetup. The clients connect to server,
    periodically run a shell script and sends results to the server. The server is capable of returning all current
    statuses (from all other clients) on a request made by a client.

    This step compiles BgChecker and generates scripts to launch all BgChecker clients which we want to have running.
    Other steps can add their periodic checks via DependencyDispatcher.register_bgchecker_script(). For each check
    this step will generate a single BgCheckerClient invocation.

    Some checks can be specific to a particular WM, so we have a concept of profile. Checks without a profile are called
    global and will be run always (in xinitrc_base). Profile-specific checks will have their own launch script which will
    have to be run separately (in WM-specific xinitrc).
    """

    class Profile:
        def __init__(self, launch_script_path, xinitrc_path, is_default_profile, is_global_profile=False):
            self.launch_script_path = FileWriter.resolve_path(launch_script_path)
            self.xinitrc_path = xinitrc_path
            self.is_default_profile = is_default_profile
            self.is_global_profile = is_global_profile

    def __init__(self, root_build_dir):
        super().__init__("BgChecker")
        self._bgchecker_build_dir = root_build_dir / "bgchecker"
        self._bgchecker_dir = Path(__file__).parent

        self._profiles = {}  # key=Profile, value=list of (script, interval) tuples
        self._global_profile = BgChckerStep.Profile(".config/LinuxSetup/run_bg_checker.sh", ".config/LinuxSetup/xinitrc_base", True, True)

        self.register_bgchecker_script(self._bgchecker_dir / "check_daemons.sh", 3)
        self.register_bgchecker_script(self._bgchecker_dir / "check_keyboard_layout.sh", 60)
        self.register_bgchecker_script(self._bgchecker_dir / "check_network_connectivity.sh", 10)
        self.register_bgchecker_script(self._bgchecker_dir / "check_network_interface.sh", 5)
        self.register_bgchecker_script(self._bgchecker_dir / "check_scripts_warnings.sh", 5)
        self.register_bgchecker_script(self._bgchecker_dir / "check_trash.sh", 15)
        self.register_bgchecker_script(self._bgchecker_dir / "check_unmatching_packages.sh", 20)
        self.register_bgchecker_script(self._bgchecker_dir / "check_updated_kernel.sh", 20)

    def register_as_dependency_listener(self, dependency_dispatcher):
        dependency_dispatcher.register_listener(self.register_bgchecker_script)
        dependency_dispatcher.register_listener(self.register_bgchecher_daemon_check_script)

    def register_bgchecker_script(self, script, interval_in_seconds, *, profile=None, **kwargs):
        entry = (script, interval_in_seconds)
        if profile is None:
            profile = self._global_profile

        if profile not in self._profiles:
            self._profiles[profile] = []
        self._profiles[profile].append(entry)

    def register_bgchecher_daemon_check_script(self, command_regex, name, **kwargs):
        self.register_bgchecker_script(f"{os.environ['SCRIPTS_PATH']}/core/linux/is_daemon_running.sh {command_regex} {name}", 3, **kwargs)

    def perform(self):
        self._build_bg_checker()
        self._generate_launch_scripts_for_profiles()

    def _build_bg_checker(self):
        ext.cmake(self._bgchecker_build_dir, cmake_args="-DCMAKE_BUILD_TYPE=RelWithDebInfo")
        ext.make(self._bgchecker_build_dir / "build")

    def _generate_launch_scripts_for_profiles(self):
        for profile, scripts in self._profiles.items():
            # Generate launch script for current profile
            lines = []
            if profile.is_global_profile:
                lines += [
                    "pkill BgChecker",
                    f"BgCheckerServer >{self._env.home() / '.log/BgCheckerServer 2>&1 &'}",
                    "",
                ]
            lines += [f'BgCheckerClient SetStatus {interval_in_seconds} "{script}" >/dev/null 2>&1 &' for script, interval_in_seconds in scripts]
            self._file_writer.write_lines(profile.launch_script_path, lines, file_type=FileType.PosixShell)

            # Call the launch script in profile-specific xinitrc script
            self._file_writer.write_section(
                profile.xinitrc_path,
                "Run BgChecker",
                [f"{profile.launch_script_path}"],
            )

            # Call the launch script in current environment, if it's the default one
            if profile.is_default_profile:
                command.run_command(f"{profile.launch_script_path} >/dev/null 2>&1", shell=True)
