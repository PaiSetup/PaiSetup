from steps.step import Step
from utils import command
import os
from enum import Enum
from pathlib import Path
from utils.log import log
from steps.gpu.nvidia_enable_vsync import main as nvidia_enable_vsync


class GpuVendor(Enum):
    Intel = 1
    Amd = 2
    Nvidia = 3


class GpuStep(Step):
    def __init__(self):
        super().__init__("Gpu")
        self._vendors = self._query_gpu_vendors()

    def perform(self):
        if self._vendors:
            vendors_string = ", ".join((v.name for v in self._vendors))
            log(f"Detected gpu vendors: {vendors_string}")
        else:
            log("No gpu vendors detected")

        if GpuVendor.Nvidia in self._vendors:
            nvidia_enable_vsync()
            self._file_writer.write_section(
                ".config/PaiSetup/xinitrc_base",
                "Enabling vsync on Nvidia",
                ["PYTHONPATH=$PAI_SETUP_ROOT $PAI_SETUP_ROOT/steps/gpu/nvidia_enable_vsync.py"],
            )

    def express_dependencies(self, dependency_dispatcher):
        vendor_specific_packages = {
            GpuVendor.Intel: [
                "vulkan-intel",
                "lib32-vulkan-intel",
                "intel-compute-runtime",
            ],
            GpuVendor.Amd: [
                "lib32-vulkan-amdgpu-pro",
                "vulkan-amdgpu-pro",
            ],
            GpuVendor.Nvidia: [
                "nvidia-dkms",
                "nvidia-utils",
                "lib32-nvidia-utils",
                "nvidia-settings",
                "opencl-nvidia",
            ],
        }

        if self._vendors:
            for vendor in self._vendors:
                dependency_dispatcher.add_packages(vendor_specific_packages[vendor])

            # Installing steam may cause a random vulkan driver to be installed as a dependency,
            # but we already selected the correct one, so we can skip automatic dependency resolution
            # for that package
            dependency_dispatcher.add_assumed_packages("lib32-vulkan-driver")
            dependency_dispatcher.add_packages(
                "vulkan-icd-loader",
                "lib32-vulkan-icd-loader",
                "steam",
            )

            dependency_dispatcher.register_homedir_file(".steam")
            dependency_dispatcher.register_homedir_file(".steampath")
            dependency_dispatcher.register_homedir_file(".steampid")
        if GpuVendor.Nvidia in self._vendors:
            dependency_dispatcher.register_homedir_file(".nv")
            dependency_dispatcher.register_homedir_file(".nvidia-settings-rc")

    def _query_gpu_vendors(self):
        lspci_output = command.run_command("lspci", return_stdout=True)
        vendors = set()
        for line in lspci_output.splitlines():
            line_lower = line.lower()
            if "vga" in line_lower or "display" in line_lower:
                if "amd" in line_lower:
                    vendors.add(GpuVendor.Amd)
                if "intel" in line_lower:
                    vendors.add(GpuVendor.Intel)
                if "nvidia" in line_lower:
                    vendors.add(GpuVendor.Nvidia)
        return vendors
