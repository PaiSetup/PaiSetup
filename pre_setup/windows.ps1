# Setup custom programs dir
$programs_dir = Read-Host -Prompt "Override programs dir. Leave empty for default $env:ProgramFiles"

# Create programs dir
if ($programs_dir -ne '') {
    mkdir $programs_dir
}

# Install Chocolatey
if ($programs_dir -ne '') {
    $env:ChocolateyInstall = "$programs_dir\Chocolatey"
    [System.Environment]::SetEnvironmentVariable("ChocolateyInstall", "$env:ChocolateyInstall", [System.EnvironmentVariableTarget]::Machine)
}
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))
Import-Module "$env:ChocolateyInstall\helpers\chocolateyProfile.psm1"
choco feature enable -n=useRememberedArgumentsForUpgrades

# Install Python
$python_install_args = ''
if ($programs_dir -ne '') {
    $python_install_args = "--packageparameters=`"/InstallDir:$programs_dir\Python3`""
} else {
    $python_install_args = "--packageparameters=`"/InstallDir:$env:ProgramFiles\Python3`""
}
choco install python311 $python_install_args --yes
Update-SessionEnvironment

# Install python libraries needed by PaiSetup
python -m pip install pywin32

# Install autohotkey
choco install autohotkey.portable --version=1.1.37.1 --yes
