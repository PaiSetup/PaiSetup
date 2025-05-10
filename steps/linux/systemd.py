import json
import os
from pathlib import Path

from steps.step import Step
from utils.command import run_command
from utils.dependency_dispatcher import push_dependency_handler
from utils.services.file_writer import FileType


class SystemdService:
    def __init__(self, name, exec_start, description=None):
        self.name = name
        self.exec_start = exec_start
        self.description = description if description is not None else name


class SystemdStep(Step):
    def __init__(self):
        super().__init__("Systemd")
        self._services = []

    @push_dependency_handler
    def add_systemd_service(self, service):
        self._services.append(service)
        self._services_dir = self._env.home() / ".config/PaiSetup/services"

    def push_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_packages("ulauncher")
        dependency_dispatcher.register_periodic_daemon_check("[a-zA-Z/]+python[23]? [a-zA-Z/]+ulauncher", "ulauncher")

    def perform(self):
        self._clean_services()
        self._setup_services()
        self._refresh_services()

    def _clean_services(self):
        self._logger.log("Cleaning existing services")
        if self._services_dir.exists():
            for file in self._services_dir.iterdir():
                file.unlink()

    def _setup_services(self):
        if not self._services:
            return

        self._services_dir.mkdir(exist_ok=True, parents=True)

        for service in self._services:
            with self._logger.indent(f"Creating {service.name} service."):
                self._logger.log("Creating .service file.")
                service_file_path = self._services_dir / f"PaiSetup_{service.name}.service"
                self._file_writer.write_lines(
                    service_file_path,
                    [self._generate_service_file_content(service)],
                    file_type=FileType.ConfigFile,
                    flush=True,
                )

                self._logger.log("Enabling service to run on boot.")
                run_command(f"systemctl --user enable {service_file_path}")

                self._logger.log("Starting service to run now.")
                run_command(f"systemctl --user enable {service_file_path}")

    def _generate_service_file_content(self, service):
        return f"""\
[Unit]
Description={service.description}
After=network.target
After=systemd-user-sessions.service
After=systemd-journald.service
StartLimitIntervalSec=1
StartLimitBurst=3

[Service]
Type=exec
ExecStart={service.exec_start}
Restart=always
RestartSec=1

[Install]
WantedBy=default.target
"""

    def _refresh_services(self):
        self._logger.log("Reloading systemctl daemon.")
        run_command("systemctl --user daemon-reload")
