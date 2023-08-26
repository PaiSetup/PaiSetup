from utils import command
from utils.log import log
from utils.os_function import windows_only

# TODO is this file needed?

def require_check(check, warning_message):
    if not check():
        log(warning_message)
        return False
    return True


@windows_only
def is_windows_activated(): # TODO remove this and call ActivateWindowsStep
    powershell_command = [
        '$output = Get-CIMInstance -query "select LicenseStatus from SoftwareLicensingProduct where LicenseStatus=1"  | Format-List LicenseStatus',
        "$isActivated = -Not [string]::IsNullOrEmpty($output)",
        "echo $isActivated",
    ]
    output = command.run_powershell_command(powershell_command, return_stdout=True, shell=True)
    return output.strip() == "True"


@windows_only
def is_admin():
    powershell_command = [
        "$currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())",
        "$isAdmin = $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)",
        "echo $isAdmin",
    ]
    output = command.run_powershell_command(powershell_command, return_stdout=True, shell=True)
    return output.strip() == "True"


@windows_only
def require_windows_activated():
    return require_check(is_windows_activated, "WARNING: Windows is not activated. Not all setup may have been performed")


@windows_only
def require_admin():
    return require_check(is_admin, "WARNING: You are not in administrator mode. Not all setup may have been performed")
