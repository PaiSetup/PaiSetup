import re

from steps.step import Step
from utils.command import *


class ActivateWindowsStep(Step):
    def __init__(self, secret_dir):
        super().__init__("ActivateWindows")
        self._secret_dir = secret_dir

    def is_windows_activated(self):
        powershell_command = [
            '$output = Get-CIMInstance -query "select LicenseStatus from SoftwareLicensingProduct where LicenseStatus=1"  | Format-List LicenseStatus',
            "$isActivated = -Not [string]::IsNullOrEmpty($output)",
            "echo $isActivated",
        ]
        output = run_powershell_command(powershell_command, stdout=Stdout.return_back(), shell=True).stdout
        return output.strip() == "True"

    def get_key(self):
        file_path = self._secret_dir / "windows11"
        try:
            with open(file_path) as file:
                key = file.readline()
                regex_section = "([A-Z0-9]{5})"
                regex = f"{regex_section}"
                if re.match(regex, key):
                    self._logger.log(f"Found a key in {file_path}")
                    return key
                else:
                    self._logger.push_warning(f"Windows 11 key found in {file_path} is invalid")
        except FileNotFoundError:
            self._logger.push_warning(f"Windows 11 key not found in {file_path}")

    def perform(self):
        if self.is_windows_activated():
            self._logger.log("Windows already activated")
            return

        key = self.get_key()
        if not key:
            return

        run_powershell_command(f"slmgr /ipk {key}")
        run_powershell_command("slmgr /ato")
