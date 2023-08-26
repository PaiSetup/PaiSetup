from steps.step import Step
from utils import command
from utils.log import log, LogIndent
from steps.windows.folders import KnownFolder


class VirtualBoxStep(Step):
    def __init__(self):
        super().__init__("VirtualBox")

    def express_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_packages("virtualbox")

        known_folders = dependency_dispatcher.get_known_folders()
        self._vm_dir = known_folders.get(KnownFolder.VirtualMachines)

        self._virtualbox_install_dir = dependency_dispatcher.get_package_info("virtualbox").install_dir

    def perform(self):
        if self._vm_dir is None:
            self._warnings.push("VM directory is not set")
            return
        if not self._virtualbox_install_dir:
            self._warnings.push("Could not find VirtualBox info")
            return
        if not self._virtualbox_install_dir.is_dir():
            self._warnings.push("VirtualBox is not installed")
            return

        log(f"Setting {self._vm_dir} as default VirtualBox machine directory")
        vboxmanage_path = self._virtualbox_install_dir / "VBoxManage.exe"
        command.run_command(f"{vboxmanage_path} setproperty machinefolder {self._vm_dir}")
