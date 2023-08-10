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

# Install Python
$python_install_args = ''
if ($programs_dir -ne '') {
    $python_install_args = "--packageparameters=`"/InstallDir:$programs_dir\Python`""
} else {
    $python_install_args = ""
}
choco install python311 $python_install_args -y

# Install autohotkey
choco install autohotkey.portable --version=1.1.37.1
