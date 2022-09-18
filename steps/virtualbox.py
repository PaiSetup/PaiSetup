from steps.step import Step
from utils import command
from utils.log import log, LogIndent


class VirtualBox(Step):
    def __init__(self):
        super().__init__("VirtualBox")
        self._vm_dir = self._env.home() / "vm"

    def express_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_packages(
            "virtualbox",
            "virtualbox-guest-iso",
            "virtualbox-host-dkms",
        )
        dependency_dispatcher.set_folder_icon(self._vm_dir, "vm")

    def perform(self):
        log(f"Setting {self._vm_dir} as default VirtualBox machine directory")
        self._vm_dir.mkdir(exist_ok=True)
        command.run_command(f"vboxmanage setproperty machinefolder {self._vm_dir}")
