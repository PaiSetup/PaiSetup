from pathlib import Path

import utils.external_project as ext
from steps.step import Step
from utils.command import *
from utils.dependency_dispatcher import push_dependency_handler
from utils.services.file_writer import FileType


class CheckMateStep(Step):
    """
    CheckMate is a client/server application written in Rust for the purposes of PaiSetup. The clients connect to server,
    periodically runs a shell script and sends results to the server. The server is capable of returning all current
    statuses (from all other clients) on a request made by a client.

    This generates scripts to launch all CheckMate clients which we want to have running. Other steps can add their periodic
    checks via DependencyDispatcher.register_periodic_check(). For each check this step will generate a single invocation
    of check_mate_client binary.

    Some checks can be specific to a particular WM, so we have a concept of profile. Checks without a profile are called
    global and will be run always (in xinitrc_base). Profile-specific checks will have their own launch script which will
    have to be run separately (in WM-specific xinitrc).
    """

    class Profile:
        def __init__(self, launch_script_path, xinitrc_path, *, is_default_profile, is_global_profile=False):
            self.launch_script_path = launch_script_path
            self.xinitrc_path = xinitrc_path
            self.is_default_profile = is_default_profile
            self.is_global_profile = is_global_profile

    class PeriodicCheck:
        def __init__(self, script, interval_in_seconds, delay_in_seconds, script_args, shell, client_name, multi_line):
            self.script = script
            self.interval_in_seconds = interval_in_seconds
            self.delay_in_seconds = delay_in_seconds
            self.script_args = script_args
            self.shell = shell
            self.client_name = client_name
            self.multi_line = multi_line

    def __init__(self, root_build_dir):
        super().__init__("CheckMate")

        self._root_build_dir = root_build_dir
        self._current_step_dir = Path(__file__).parent
        self._tcp_port = 50198
        self._profiles = {}  # key=Profile, value=list of PeriodicCheck
        self._global_profile = CheckMateStep.Profile(
            self._file_writer.resolve_path(".config/PaiSetup/run_check_mate.sh"),
            ".config/PaiSetup/xinitrc_base",
            is_default_profile=True,
            is_global_profile=True,
        )

        self.register_periodic_check(self._current_step_dir / "check_keyboard_layout.sh", 60, client_name="KeyboardLayout")
        self.register_periodic_check(self._current_step_dir / "check_network_connectivity.sh", 10, client_name="NetworkConnectivity")
        self.register_periodic_check(self._current_step_dir / "check_network_interface.sh", 5, client_name="NetworkInterface")
        self.register_periodic_check(self._current_step_dir / "check_scripts_warnings.sh", 5, client_name="ScriptsWarnings")
        self.register_periodic_check(self._current_step_dir / "check_trash.sh", 15, client_name="Trash")
        self.register_periodic_check(self._current_step_dir / "check_unmatching_packages.sh", 20, multi_line=True, client_name="UnmatchingPackages")
        self.register_periodic_check(self._current_step_dir / "check_updated_kernel.sh", 20, client_name="UpdatedKernel")

    @push_dependency_handler
    def register_periodic_check(
        self,
        script,
        interval_in_seconds,
        *,
        profile=None,
        delay_in_seconds=None,
        script_args="",
        shell=False,
        client_name=None,
        multi_line=False,
    ):
        if profile is None:
            profile = self._global_profile
        if profile not in self._profiles:
            self._profiles[profile] = []

        check = CheckMateStep.PeriodicCheck(script, interval_in_seconds, delay_in_seconds, script_args, shell, client_name, multi_line)
        self._profiles[profile].append(check)

    @push_dependency_handler
    def register_periodic_daemon_check(self, command_regex, name, **kwargs):
        script = self._current_step_dir / "is_daemon_running.sh"
        script_args = f"{command_regex} {name}"
        self.register_periodic_check(script, 3, script_args=script_args, **kwargs)

    def perform(self):
        self._install()
        self._setup_launch_script()

    def _install(self):
        dst_dir = self._root_build_dir / "check_mate"
        ext.download_github_release(
            "DziubanMaciej",
            "CheckMate",
            dst_dir,
            "v0.4.0",
            "check_mate_linux_0.4.0.zip",
            re_download=False,
        )

        binary_dir = dst_dir / "check_mate_linux_0.4.0"
        self._file_writer.write_symlink_executable(binary_dir / "check_mate_client", "check_mate_client")
        self._file_writer.write_symlink_executable(binary_dir / "check_mate_server", "check_mate_server")

    def _setup_launch_script(self):
        for profile, checks in self._profiles.items():
            # Generate launch script for current profile
            lines = []
            if profile.is_global_profile:
                lines += [
                    "pkill -f check_mate_client",
                    "pkill -f check_mate_server",
                    "",
                    f"check_mate_server -p {self._tcp_port} >{self._env.home() / '.log/check_mate_server 2>&1 &'}",
                    "",
                ]
            for check in checks:
                line = "check_mate_client watch"
                line += f' "{check.script}" {check.script_args}'
                line += f" --"
                if check.delay_in_seconds is not None:
                    line += f" -d {1000*check.delay_in_seconds}"
                if check.client_name is not None:
                    line += f" -n {check.client_name}"
                line += f" -w {1000*check.interval_in_seconds}"
                line += f" -p {self._tcp_port}"
                if check.multi_line:
                    line += f" -m MultiLineError"
                if check.shell:
                    line += " -s 1"
                line += " >/dev/null 2>&1 &"
                lines.append(line)
            self._file_writer.write_lines(profile.launch_script_path, lines, file_type=FileType.PosixShell, flush=True)

            # Call the launch script in profile-specific xinitrc script
            self._file_writer.write_section(
                profile.xinitrc_path,
                "Run check_mate",
                [f"{profile.launch_script_path}"],
            )

            # Call the launch script in current environment, if it's the default one
            if profile.is_default_profile:
                print(profile.launch_script_path)
                run_command(f"{profile.launch_script_path} >/dev/null 2>&1", shell=True)
