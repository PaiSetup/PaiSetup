from steps.step import Step
from utils import command
from utils.log import log
import re

class ActivateWindowsStep(Step):
    def __init__(self, root_dir):
        super().__init__("ActivateWindows")
        self._root_dir = root_dir

    def is_windows_activated(self):
        powershell_command = [
            '$output = Get-CIMInstance -query "select LicenseStatus from SoftwareLicensingProduct where LicenseStatus=1"  | Format-List LicenseStatus',
            "$isActivated = -Not [string]::IsNullOrEmpty($output)",
            "echo $isActivated",
        ]
        output = command.run_powershell_command(powershell_command, return_stdout=True, shell=True)
        return output.strip() == "True"

    def get_key(self):
        file_path = self._root_dir / ".key_windows10"
        try:
            with open(file_path) as file:
                key = file.readline()
                regex_section = "([A-Z0-9]{5})"
                regex = f"{regex_section}"
                if re.match(regex, key):
                    log(f"Found a key in {file_path}")
                    return key
                else:
                    log(f"Key found in {file_path} is invalid")
        except FileNotFoundError:
            log(f"Key not found in {file_path}")


    def perform(self):
        if self.is_windows_activated():
            log("Windows already activated")
            return

        key = self.get_key()
        if not key:
            return

        command.run_powershell_command(f'slmgr /ipk {key}')
        command.run_powershell_command('slmgr /ato')
