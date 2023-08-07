# Get target folder
$packageParams = Get-PackageParameters
$folder = $packageParams.folder
if (-Not $folder) {
    throw "Specify /folder package parameter"
}

# Cache target folder
$cacheFilePath = (Split-Path -parent $MyInvocation.MyCommand.Definition) + "\folderToDelete.txt"
echo "$folder" >> $cacheFilePath

# Download and unzip package
$args = @{
    PackageName   = $packageName
    Url           = "https://github.com/InternalMD/WindowsHandies/releases/download/1.6/WindowsHandies.zip"
    UnzipLocation = $folder
}
Install-ChocolateyZipPackage @args

# Create shims
Install-BinFile Audioswitch     $folder\Audioswitch.exe
Install-BinFile Iconfigure      $folder\Iconfigure.exe
Install-BinFile KnownFolders    $folder\KnownFolders.exe
Install-BinFile VeracryptSwitch $folder\VeracryptSwitch.exe
