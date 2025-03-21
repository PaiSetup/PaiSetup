from steps.step import Step
from steps.windows.folders import KnownFolder
from utils.command import *


class VirtualBoxStep(Step):
    def __init__(self):
        super().__init__("VirtualBox")

    def push_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_packages("virtualbox")

    def pull_dependencies(self, dependency_dispatcher):
        known_folders = dependency_dispatcher.get_known_folders()
        self._vm_dir = known_folders.get(KnownFolder.VirtualMachines)
        self._virtualbox_install_dir = dependency_dispatcher.get_package_info("virtualbox").install_dir

    def perform(self):
        if self._vm_dir is None:
            self._logger.push_warning("VM directory is not set")
            return
        if not self._virtualbox_install_dir:
            self._logger.push_warning("Could not find VirtualBox info")
            return
        if not self._virtualbox_install_dir.is_dir():
            self._logger.push_warning("VirtualBox is not installed")
            return

        self._logger.log(f"Setting {self._vm_dir} as default VirtualBox machine directory")
        vboxmanage_path = self._virtualbox_install_dir / "VBoxManage.exe"
        run_command(f"{vboxmanage_path} setproperty machinefolder {self._vm_dir}")
