from steps.step import Step
from utils import command
from utils.log import log
from pathlib import Path


class LightDmStep(Step):
    def __init__(self):
        super().__init__("LightDm")

    def setup_required_packages(self, packages_step):
        packages_step.add_packages(
            "lightdm",
            "lightdm-gtk-greeter",
            "xinit-xsession",
        )

    def _perform_impl(self):
        # Enable service
        service_name = "lightdm.service"
        log(f"Enabling {service_name}")
        command.run_command(f"sudo systemctl enable {service_name}")

        # Configure
        current_step_dir = Path(__file__).parent
        config_path = "/usr/share/lightdm"
        log(f"Setting up config files in {config_path}")
        command.run_command(f"sudo mkdir -p {config_path}/lightdm.conf.d")
        command.run_command(f"sudo mkdir -p {config_path}/lightdm-gtk-greeter.conf.d")
        command.run_command(f"sudo cp {current_step_dir}/lightdm.conf {config_path}/lightdm.conf.d/")
        command.run_command(f"sudo cp {current_step_dir}/lightdm-gtk-greeter.conf {config_path}/lightdm-gtk-greeter.conf.d/")
        command.run_command(f"sudo cp {current_step_dir}/wallpaper.jpg {config_path}/")
