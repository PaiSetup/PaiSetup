import pythoncom
from win32com.shell import shell, shellcon


def create_shortcut(
    shortcut_path,
    target_path,
    *,
    target_args=None,
    as_admin=False,
):
    """
    Mostly blindly copied from https://stackoverflow.com/a/37063259 and slightly altered.
    """
    shortcut = pythoncom.CoCreateInstance(shell.CLSID_ShellLink, None, pythoncom.CLSCTX_INPROC_SERVER, shell.IID_IShellLink)
    shortcut.SetPath(str(target_path))
    if target_args is not None:
        shortcut.SetArguments(target_args)
    if as_admin:
        shortcut_data = shortcut.QueryInterface(shell.IID_IShellLinkDataList)
        shortcut_data.SetFlags(shortcut_data.GetFlags() | shellcon.SLDF_RUNAS_USER)
    file = shortcut.QueryInterface(pythoncom.IID_IPersistFile)

    if shortcut_path.suffix != ".lnk":
        shortcut_path = str(shortcut_path) + ".lnk"
    else:
        shortcut_path = str(shortcut_path)
    file.Save(shortcut_path, 0)
