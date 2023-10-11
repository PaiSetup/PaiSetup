from steps.step import Step
from utils import command
from pathlib import Path


class LightDmStep(Step):
    def __init__(self):
        super().__init__("LightDm")

    def express_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_packages(
            "lightdm",
            "lightdm-gtk-greeter",
        )
        dependency_dispatcher.register_homedir_file(".dmrc")

    def perform(self):
        # Enable service
        service_name = "lightdm.service"
        self._logger.log(f"Enabling {service_name}")
        command.run_command(f"sudo systemctl enable {service_name}")

        # Configure
        current_step_dir = Path(__file__).parent
        config_path = "/usr/share/lightdm"
        self._logger.log(f"Setting up config files in {config_path}")
        command.run_command(f"sudo mkdir -p {config_path}/lightdm.conf.d")
        command.run_command(f"sudo mkdir -p {config_path}/lightdm-gtk-greeter.conf.d")
        command.run_command(f"sudo cp {current_step_dir}/lightdm.conf {config_path}/lightdm.conf.d/")
        command.run_command(f"sudo cp {current_step_dir}/lightdm-gtk-greeter.conf {config_path}/lightdm-gtk-greeter.conf.d/")
        command.run_command(f"sudo cp {current_step_dir}/wallpaper.jpg {config_path}/")
