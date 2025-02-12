from steps.step import Step
from utils.dependency_dispatcher import push_dependency_handler
from utils.windows.windows_registry import *


class ExplorerStep(Step):
    def __init__(self):
        super().__init__("Explorer")
        self._quick_access_folder_for_removal = []
        self._quick_access_folder_for_addition = []

    @push_dependency_handler
    def remove_folder_from_quick_access(self, folder):
        self._quick_access_folder_for_removal.append(folder)

    @push_dependency_handler
    def add_folder_to_quick_access(self, folder):
        self._quick_access_folder_for_addition.append(folder)

    def perform(self):
        self._setup_system_icons_on_desktop()
        self._setup_shown_files()
        self._setup_taskbar()
        self._setup_context_menus()
        self._set_dark_theme()
        self._setup_quick_access()
        self._remove_bloat_folders()
        # self._reset_explorer()

    def _setup_system_icons_on_desktop(self):
        self._logger.log("Setting up system icons on desktop")

        # Show "This PC" on Desktop
        set_registry_value_dword(
            HKCU, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\HideDesktopIcons\NewStartPanel", "{20D04FE0-3AEA-1069-A2D8-08002B30309D}", "0"
        )

    def _setup_shown_files(self):
        self._logger.log("Setting up shown files")
        set_registry_value_dword(HKCU, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced", "Hidden", 1)
        set_registry_value_dword(HKCU, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced", "HideFileExt", 0)
        set_registry_value_dword(HKCU, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer", "ShowFrequent", 0)
        set_registry_value_dword(HKCU, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer", "ShowRecent", 0)

    def _setup_taskbar(self):
        self._logger.log("Cleaning taskbar")
        set_registry_value_dword(HKCU, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Search", "SearchboxTaskbarMode", 0)
        set_registry_value_dword(HKCU, r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced", "ShowCortanaButton", 0)
        set_registry_value_dword(HKCU, r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced", "ShowTaskViewButton", 0)
        set_registry_value_dword(HKCU, r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced\People", "PeopleBand", 0, create_keys=True)
        # set_registry_value_dword(HKCU, r"Software\Microsoft\Windows\CurrentVersion\Feeds", "IsFeedsAvailable", 0)
        set_registry_value_dword(HKCU, r"Software\Microsoft\Windows\CurrentVersion\Feeds", "EnableFeeds", 0)
        # set_registry_value_dword(HKCU, r"Software\Microsoft\Windows\CurrentVersion\Feeds", "ShellFeedsTaskbarViewMode", 2)
        set_registry_value_dword(HKCU, r"SOFTWARE\Microsoft\Windows\CurrentVersion\PenWorkspace", "PenWorkspaceButtonDesiredVisibility", 0)
        set_registry_value_dword(HKLM, r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer", "NoTaskGrouping", 1)

    def _setup_context_menus(self):
        self._logger.log("Cleaning context menus")
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
        self._logger.log("Enabling dark theme")
        set_registry_value_dword(HKCU, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize", "SystemUsesLightTheme", 0)
        set_registry_value_dword(HKCU, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize", "AppsUseLightTheme", 0)

    def _setup_quick_access(self):
        if len(self._quick_access_folder_for_removal) == 0 and len(self._quick_access_folder_for_addition) == 0:
            return

        self._logger.log("Setting up quick access")
        powershell_command = [
            "$object = New-Object -com shell.application",
            "$quickAccessItems = $object.Namespace('shell:::{679F85CB-0220-4080-B29B-5540CC05AAB6}').Items()",
        ]
        for folder in self._quick_access_folder_for_removal:
            powershell_command += [
                f"$item = ($quickAccessItems | Where-Object {{ $_.Path -EQ '{folder}' }})",
                "if ($item) { $item.InvokeVerb('unpinfromhome') }",
            ]
        for folder in self._quick_access_folder_for_addition:
            powershell_command += [f"$object.Namespace('{folder}').Self.InvokeVerb('pintohome')"]
        run_powershell_command(powershell_command)

    def _remove_bloat_folders(self):
        self._logger.log("Removing bloat folders")
        delete_registry_sub_key_tree(
            HKLM, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\MyComputer\NameSpace", "{0DB7E03F-FC29-4DC6-9020-FF41B59E513A}"
        )
        delete_registry_sub_key_tree(
            HKLM, r"SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\Explorer\MyComputer\NameSpace", "{0DB7E03F-FC29-4DC6-9020-FF41B59E513A}"
        )

    def _reset_explorer(self):
        self._logger.log("Resetting explorer")
        run_powershell_command("stop-process -name explorer -force")
