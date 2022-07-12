from steps.step import Step
import os
import utils.external_project as ext
from utils.log import log, LogIndent
from utils import command
from pathlib import Path


class BgChckerStep(Step):
    def __init__(self, root_build_dir):
        super().__init__("BgChecker")
        self._bgchecker_build_dir = root_build_dir / "bgchecker"
        self._bgchecker_dir = Path(__file__).parent
        self._bgchecker_script = self._bgchecker_dir / "run.sh"
        self._scripts = []

        self.register_bgchecker_script(self._bgchecker_dir / "check_daemons.sh", 3)
        self.register_bgchecker_script(self._bgchecker_dir / "check_keyboard_layout.sh", 60)
        self.register_bgchecker_script(self._bgchecker_dir / "check_network_connectivity.sh", 10)
        self.register_bgchecker_script(self._bgchecker_dir / "check_network_interface.sh", 5)
        self.register_bgchecker_script(self._bgchecker_dir / "check_scripts_warnings.sh", 5)
        self.register_bgchecker_script(self._bgchecker_dir / "check_unmatching_packages.sh", 20)
        self.register_bgchecker_script(self._bgchecker_dir / "check_updated_kernel.sh", 20)

    def register_as_dependency_listener(self, dependency_dispatcher):
        dependency_dispatcher.register_listener(self.register_bgchecker_script)

    def express_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_dotfile_section(
            ".xinitrc",
            "Run BgChecker",
            [f"{self._bgchecker_script}"],
        )

    def register_bgchecker_script(self, script, interval_in_seconds):
        self._scripts.append((script, interval_in_seconds))

    def _perform_impl(self):
        ext.cmake(self._bgchecker_build_dir, cmake_args="-DCMAKE_BUILD_TYPE=RelWithDebInfo")
        ext.make(self._bgchecker_build_dir / "build")

        log("Generating run.sh script to launch BgChecker")
        with open(self._bgchecker_script, "w") as run_script_file:
            run_script_file.write("#!/bin/sh\n")
            run_script_file.write("pkill BgChecker\n")
            with LogIndent():
                for script, interval_in_seconds in self._scripts:
                    log(f"Run \"{script}\" every {interval_in_seconds} seconds")
                    run_script_file.write(f"BgCheckerClient SetStatus {interval_in_seconds} \"{script}\" >/dev/null 2>&1 &\n")
                run_script_file.write("BgCheckerServer &\n")
        command.run_command(f"sudo chmod +x {self._bgchecker_script}")

        log("Running run.sh script")
        command.run_command(f"{self._bgchecker_script} >/dev/null 2>&1", shell=True)
