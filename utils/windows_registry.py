from utils.os_function import require_windows

require_windows()

import winreg

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

    with _open_registry_key(hive, key, winreg.KEY_ALL_ACCESS) as key:
        delete(key, subkey_name)


def delete_registry_value(hive, key, value_name):
    with _open_registry_key(hive, key, winreg.KEY_SET_VALUE) as key:
        try:
            winreg.DeleteValue(key, value_name)
        except FileNotFoundError:
            # If it doesn't exist, it's ok
            pass


def get_registry_value(hive, key, value_name):
    with _open_registry_key(hive, key, winreg.KEY_QUERY_VALUE) as key:
        if value_name is None:
            value_name = ""
        return winreg.QueryValueEx(key, value_name)


def set_registry_value_string(hive, key, value_name, value, create_keys=False):
    with _open_registry_key(hive, key, winreg.KEY_SET_VALUE, create_keys=create_keys) as key:
        winreg.SetValueEx(key, value_name, 0, winreg.REG_SZ, value)


def _open_registry_key(hive, key, access, *, create_keys=False):
    if create_keys:
        return winreg.CreateKeyEx(hive, key, 0, access)
    else:
        return winreg.OpenKey(hive, key, 0, access)

def set_registry_value_dword(hive, key, value_name, value, create_keys=False):
    value = int(value)
    with _open_registry_key(hive, key, winreg.KEY_SET_VALUE, create_keys=create_keys) as key:
        winreg.SetValueEx(key, value_name, 0, winreg.REG_DWORD, value)
