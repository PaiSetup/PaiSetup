from steps.step import Step
from utils.command import *


class VirtualBoxStep(Step):
    def __init__(self):
        super().__init__("VirtualBox")
        self._vm_dir = self._env.home() / "vm"

    def push_dependencies(self, dependency_dispatcher):
        raise NotImplementedError("Virtual box is a broken package")
        dependency_dispatcher.add_packages(
            "virtualbox",
            "virtualbox-guest-iso",
            "virtualbox-host-dkms",
        )
        dependency_dispatcher.register_homedir_file("vm")
        dependency_dispatcher.set_folder_icon(self._vm_dir, "vm")

    def perform(self):
        self._logger.log(f"Setting {self._vm_dir} as default VirtualBox machine directory")
        self._vm_dir.mkdir(exist_ok=True)
        run_command(f"vboxmanage setproperty machinefolder {self._vm_dir}")
