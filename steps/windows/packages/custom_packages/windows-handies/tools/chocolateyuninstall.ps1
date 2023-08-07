# Get target folder
$cacheFilePath = (Split-Path -parent $MyInvocation.MyCommand.Definition) + "\folderToDelete.txt"
$folder = Get-Content $cacheFilePath

# Remove shims
Uninstall-BinFile Audioswitch     $folder\Audioswitch.exe
Uninstall-BinFile Iconfigure      $folder\Iconfigure.exe
Uninstall-BinFile KnownFolders    $folder\KnownFolders.exe
Uninstall-BinFile VeracryptSwitch $folder\VeracryptSwitch.exe

# Remove package
Remove-Item -Recurse -Force $folder