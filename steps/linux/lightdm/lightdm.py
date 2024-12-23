from pathlib import Path

from steps.step import Step
from utils.command import *


class LightDmStep(Step):
    def __init__(self):
        super().__init__("LightDm")

    def express_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_packages(
            "lightdm",
            "lightdm-gtk-greeter",
            "numlockx",
        )
        dependency_dispatcher.register_homedir_file(".dmrc")

    def perform(self):
        self._enable_service()
        self._configure()

    def _enable_service(self):
        # Check, if we can skip
        try:
            out = run_command("systemctl status display-manager", stdout=Stdout.return_back()).stdout
            out = out.splitlines()
            out = out[0]
            if "lightdm.service" in out:
                return
        except CommandError:
            # No display manager detected
            pass

        service_name = "lightdm.service"
        self._logger.log(f"Enabling {service_name}")
        run_command(f"sudo systemctl enable {service_name}")

    def _configure(self):
        current_step_dir = Path(__file__).parent
        config_path = "/usr/share/lightdm"
        self._logger.log(f"Setting up config files in {config_path}")
        run_command(f"sudo mkdir -p {config_path}/lightdm.conf.d")
        run_command(f"sudo mkdir -p {config_path}/lightdm-gtk-greeter.conf.d")
        run_command(f"sudo cp {current_step_dir}/lightdm.conf {config_path}/lightdm.conf.d/")
        run_command(f"sudo cp {current_step_dir}/lightdm-gtk-greeter.conf {config_path}/lightdm-gtk-greeter.conf.d/")
        run_command(f"sudo cp {current_step_dir}/wallpaper.jpg {config_path}/")
