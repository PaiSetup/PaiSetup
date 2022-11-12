from steps.step import Step
import os


class BluetoothStep(Step):
    def __init__(self):
        super().__init__("Bluetooth")
        self.disable_suspending_command = ""

    def express_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_packages(
            "bluez",  # Core driver
            "bluez-utils",  # For bluetoothctl
            "rofi",  # For panel.sh script
        )

    def perform(self):
        self._file_writer.write_section(
            ".config/LinuxSetup/xinitrc_base",
            "Auto connect to trusted bluetooth devices",
            ["$LINUX_SETUP_ROOT/steps/bluetooth/connect_to_trusted.sh &"],
        )


"""
I tried to write a script for pairing BT devices, but bluetoothctl is too messed up and it's really hard to script, considering
how rarely I actually have to pair devices.

It is explain very well on arch wiki and takes a minute to do
    https://wiki.archlinux.org/title/bluetooth_headset#Configuration_via_CLI

Commands for troubleshooting when bluetoothctl throws errors:
    rfkill block bluetooth
    rfkill unblock bluetooth
    rmmod btusb
    modprobe btusb
    systemctl restart bluetooth.service
"""
