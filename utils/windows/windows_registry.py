from utils.os_function import require_windows

require_windows()

import winreg

from utils.command import *

HKCU = winreg.HKEY_CURRENT_USER
HKLM = winreg.HKEY_LOCAL_MACHINE
HKCR = winreg.HKEY_CLASSES_ROOT


def delete_registry_sub_key_tree(hive, key, subkey_name):
    def delete(key, subkey_name):
        try:
            # Remove subsubkeys (subkeys of current subkey)
            with _open_registry_key(key, subkey_name, winreg.KEY_ALL_ACCESS) as subkey:
                number_of_subsubkeys = winreg.QueryInfoKey(subkey)[0]
                for subsubkey_index in range(number_of_subsubkeys):
                    subsubkey_name = winreg.EnumKey(subkey, 0)
                    delete(subkey, subsubkey_name)

            # Remove the curent subkey
            winreg.DeleteKey(key, subkey_name)
        except FileNotFoundError:
            # If it doesn't exist, it's ok
            pass

    try:
        with _open_registry_key(hive, key, winreg.KEY_ALL_ACCESS) as key:
            delete(key, subkey_name)
    except FileNotFoundError:
        # If it doesn't exist, it's ok
        pass


def delete_registry_value(hive, key, value_name=None):
    if value_name is None:
        value_name = ""

    try:
        with _open_registry_key(hive, key, winreg.KEY_SET_VALUE) as key:
            winreg.DeleteValue(key, value_name)
    except FileNotFoundError:
        # If it doesn't exist, it's ok
        pass


def get_registry_value(hive, key, value_name=None, missing_ok=False):
    if value_name is None:
        value_name = ""

    try:
        with _open_registry_key(hive, key, winreg.KEY_QUERY_VALUE) as key:
            return winreg.QueryValueEx(key, value_name)[0]
    except FileNotFoundError:
        if missing_ok:
            return None
        else:
            raise


def set_registry_value_string(hive, key, value_name, value, create_keys=False):
    if value_name is None:
        value_name = ""

    with _open_registry_key(hive, key, winreg.KEY_SET_VALUE, create_keys=create_keys) as key:
        winreg.SetValueEx(key, value_name, 0, winreg.REG_SZ, value)


def _open_registry_key(hive, key, access, *, create_keys=False):
    if create_keys:
        return winreg.CreateKeyEx(hive, key, 0, access)
    else:
        return winreg.OpenKey(hive, key, 0, access)


def set_registry_value_dword(hive, key, value_name, value, create_keys=False):
    if value_name is None:
        value_name = ""

    value = int(value)
    with _open_registry_key(hive, key, winreg.KEY_SET_VALUE, create_keys=create_keys) as key:
        winreg.SetValueEx(key, value_name, 0, winreg.REG_DWORD, value)


def delete_registry_user_choice(hive, extension):
    """
    UserChoice key for extension associations is protected with a permission. It cannot be removed with
    delete_registry_sub_key_tree. A proper solution would be to remove this permission, but that's not that
    easy. For now there is this nasty workaround. For some reason DeleteSubKey in Powershell is able to
    delete UserChoice key anyway. Seems like a bug - DeleteSubKeyTreeTree and Remove-Item do not work.
    """

    try:
        get_registry_value(hive, rf"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\FileExts\{extension}\UserChoice", missing_ok=True)
    except FileNotFoundError:
        return

    if hive == HKCU:
        hive = "[Microsoft.Win32.Registry]::CurrentUser"
    elif hive == HKLM:
        hive = "[Microsoft.Win32.Registry]::LocalMachine"
    else:
        raise ValueError("Unsupported hive")

    powershell_command = [
        f"$key = {hive}.OpenSubKey('SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\FileExts\{extension}', $True)",
        "if ($key) {",
        "    $key.DeleteSubKey('UserChoice', $False)",
        "    $key.Close()",
        "}",
    ]
    run_powershell_command(powershell_command)
