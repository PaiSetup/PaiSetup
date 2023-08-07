from steps.step import Step
from utils.checks import *
from utils.windows_registry import *


class ExplorerStep(Step):
    def __init__(self):
        super().__init__("Explorer")

    def perform(self):
        self._setup_shown_files()
        self._setup_taskbar()
        self._setup_context_menus()
        self._set_dark_theme()
        self._remove_bloat_folders()
        # self._reset_explorer()

    def _setup_shown_files(self):
        log("Setting up shown files")
        set_registry_value_dword(HKCU, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced", "Hidden", 1)
        set_registry_value_dword(HKCU, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced", "HideFileExt", 0)
        set_registry_value_dword(HKCU, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer", "ShowFrequent", 0)
        set_registry_value_dword(HKCU, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer", "ShowRecent", 0)

    def _setup_taskbar(self):
        log("Cleaning taskbar")
        set_registry_value_dword(HKCU, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Search", "SearchboxTaskbarMode", 0)
        set_registry_value_dword(HKCU, r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced", "ShowCortanaButton", 0)
        set_registry_value_dword(HKCU, r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced", "ShowTaskViewButton", 0)
        set_registry_value_dword(HKCU, r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced\People", "PeopleBand", 0)
        set_registry_value_dword(HKCU, r"Software\Microsoft\Windows\CurrentVersion\Feeds", "ShellFeedsTaskbarViewMode", 2)
        set_registry_value_dword(HKCU, r"SOFTWARE\Microsoft\Windows\CurrentVersion\PenWorkspace", "PenWorkspaceButtonDesiredVisibility", 0)
        set_registry_value_dword(HKLM, r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer", "NoTaskGrouping", 1)

    def _setup_context_menus(self):
        log("Cleaning context menus")
        delete_registry_sub_key_tree(HKCR, r"Directory\Background\shell", "AnyCode")
        delete_registry_sub_key_tree(HKCR, r"Directory\Background\shellex\ContextMenuHandlers", "NvCplDesktopContext")
        delete_registry_sub_key_tree(HKCR, r"Directory\shell", "AddToPlaylistVLC")
        delete_registry_sub_key_tree(HKCR, r"Directory\shell", "PlayWithVLC")
        delete_registry_sub_key_tree(HKCR, r"Directory\shell", "AnyCode")
        delete_registry_sub_key_tree(HKCR, r"Directory\shell", "Durchsuchen mit &IrfanView")
        delete_registry_sub_key_tree(HKCR, r"Directory\shellex\ContextMenuHandlers", "EPP")
        delete_registry_sub_key_tree(HKCR, r"Directory\shellex\ContextMenuHandlers", "FormatFactoryShell")
        delete_registry_sub_key_tree(HKCR, r"Directory\shellex\ContextMenuHandlers", "MEGA (Context menu)")
        delete_registry_sub_key_tree(HKCR, r"Directory\shellex\ContextMenuHandlers", "Mp3tagShell")
        delete_registry_sub_key_tree(HKCR, r"Directory\shellex\ContextMenuHandlers", "DesktopDockShellExt")
        delete_registry_sub_key_tree(HKCR, r"Folder\shellex\ContextMenuHandlers", "Library Location")
        delete_registry_sub_key_tree(HKCR, r"Folder\shellex\ContextMenuHandlers", "DesktopDockShellExt")
        delete_registry_sub_key_tree(HKCR, r"*\shellex\ContextMenuHandlers", "FormatFactoryShell")
        delete_registry_sub_key_tree(HKCR, r"*\shellex\ContextMenuHandlers", "EPP")
        delete_registry_sub_key_tree(HKCR, r"*\shellex\ContextMenuHandlers", "MEGA (Context menu)")
        set_registry_value_string(
            HKLM,
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Shell Extensions\Blocked",
            "{9F156763-7844-4DC4-B2B1-901F640F5155}",
            "",
            create_keys=True,
        )

    def _set_dark_theme(self):
        log("Enabling dark theme")
        set_registry_value_dword(HKCU, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize", "SystemUsesLightTheme", 0)
        set_registry_value_dword(HKCU, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize", "AppsUseLightTheme", 0)

    def _remove_bloat_folders(self):
        log("Removing bloat folders")
        delete_registry_sub_key_tree(
            HKLM, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\MyComputer\NameSpace", "{0DB7E03F-FC29-4DC6-9020-FF41B59E513A}"
        )
        delete_registry_sub_key_tree(
            HKLM, r"SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\Explorer\MyComputer\NameSpace", "{0DB7E03F-FC29-4DC6-9020-FF41B59E513A}"
        )

    def _reset_explorer(self):
        log("Resetting explorer")
        command.run_powershell_command("stop-process -name explorer -force")
