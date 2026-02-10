from steps.step import Step
from utils.windows.windows_registry import *


class ExtensionsStep(Step):
    r"""
    Association of extensions with applications and other shell features are all stored in registry.
    There seems to be no easy way to alter them via API calls, so the registry has to be manually
    fiddled with. Below are some notes about how it all works.

    HKCU\SOFTWARE\Classes and HKLM\SOFTWARE\Classes contains the most important data about extensions.
    There is a separate subkey for each extension, although metadata does not lie directly in this
    key. Instead, its default value is a name of another key, which is also in
    HKCU\SOFTWARE\Classes and contains app-specific information (e.g. icon, command to open the file,
    description of the application, etc.). So the value in HKLM\SOFTWARE\Classes\<extension> could be
    treated as a pointer to the app-specific key. Not sure how it's actually called, but let's call it
    application key. This mechanism is probably made to allow reusing app-specific data for multiple
    extensions.

    HKCR is a merged view of HKCU\SOFTWARE\Classes and HKLM\SOFTWARE\Classes. It can contain keys
    and values from both of them (HKCU is more important). This is created mainly for compatibility
    reasons and we shouldn't set values to HKCR, but rather HKLM or HKCU directly. When removing
    values, they should be removed from both HKLM and HKCU to be sure they are gone.

    HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\FileExts (or HKLM counterpart) contains
    additional information about extension associations. There is a separate subkey for each extension.

    Some resources:
        https://learn.microsoft.com/en-us/windows/win32/sysinfo/hkey-classes-root-key
        https://learn.microsoft.com/en-us/windows/win32/shell/fa-verbs
    """

    def __init__(self):
        super().__init__("Extensions")
        self._app_key_npp = "PaiSetupNpp"

    def push_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_packages("notepadplusplus")

    def pull_dependencies(self, dependency_dispatcher):
        self._npp_install_dir = dependency_dispatcher.get_package_info("notepadplusplus").install_dir

    def perform(self):
        # fmt: off
        self._logger.log("Associating extensions with Powershell")
        self._setup_extension_powershell(".ps1", "Powershell script", True)

        # fmt: off
        npp_path = self._npp_install_dir / "notepad++.exe"
        self._logger.log(f"Associating extensions with Notepad++ ({npp_path})")
        extensions_for_npp = [
            (".txt",           "Text file (.txt)",     True),
            (".cmake",         None,                   False),
            (".cpp",           "C++ file (.cpp)",      True),
            (".gitattributes", None,                   False),
            (".gitignore",     None,                   False),
            (".gitmodules",    None,                   False),
            (".h",             "C++ header file (.h)", True),
            (".inl",           None,                   False),
            (".java",          None,                   False),
            (".json",          None,                   False),
            (".log",           None,                   False),
            (".lua",           None,                   False),
            (".md",            "Markdown file",        False),
            (".nuspec",        None,                   False),
            (".psm1",          "Powershell module",    False),
            (".py",            "Python file (.py)",    True),
            (".yaml",          None,                   False),
            (".yml",           None,                   False),
        ]
        # fmt: on
        for extension, description, new_file_entry in extensions_for_npp:
            self._setup_extension_npp(npp_path, extension, description, new_file_entry)

        self._logger.log("Removing unneeded context menu entries")
        new_file_entries_to_remove = [".rtf", ".docx", ".pptx", ".xlsx", ".rar", ".zip", ".bmp", ".rtf"]
        for extension in new_file_entries_to_remove:
            self._clear_new_file_entry(extension)

    def _clear_new_file_entry(self, extension):
        """
        This method removes possibility to create new file with given extension from the context menu.
        Some programs typically register hooks for that and we usually do not want it.
        """

        # It can be configured ShellNew key
        delete_registry_sub_key_tree(HKCU, rf"SOFTWARE\Classes\{extension}", "ShellNew")
        delete_registry_sub_key_tree(HKLM, rf"SOFTWARE\Classes\{extension}", "ShellNew")

        application_key = get_registry_value(HKCR, extension, missing_ok=True)
        if application_key is not None:
            # It can also be configured inside app-specific key (e.g. Microsoft Word)
            delete_registry_sub_key_tree(HKCU, rf"SOFTWARE\Classes\{application_key}", "ShellNew")
            delete_registry_sub_key_tree(HKLM, rf"SOFTWARE\Classes\{application_key}", "ShellNew")

            # It can also be configured in a subkey with a name equal to application key
            delete_registry_sub_key_tree(HKCU, rf"SOFTWARE\Classes\{extension}\{application_key}", "ShellNew")
            delete_registry_sub_key_tree(HKLM, rf"SOFTWARE\Classes\{extension}\{application_key}", "ShellNew")

    def _clear_user_choice(self, extension):
        """
        This method removes association of extension to an application. This is created when user selects an
        application in "Open with..." menu and checks "Always use this app" checkbox. It is difficult to set
        UserChoice to a desired value, because it is secured with a hash. However, if we delete it, the user
        will be presented with a choice the next time they try to open the file with this extension.
        """

        # UserChoice field is protected with a permission and for now we are removing it with a workaround.
        delete_registry_user_choice(HKCU, extension)
        delete_registry_user_choice(HKLM, extension)

        # Now we can remove the rest of the keys, which are not protected
        delete_registry_sub_key_tree(HKCU, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\FileExts", extension)
        delete_registry_sub_key_tree(HKLM, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\FileExts", extension)

    def _create_new_file_entry(self, extension):
        set_registry_value_string(HKCU, rf"SOFTWARE\Classes\{extension}\ShellNew", "NullFile", "", create_keys=True)

    def _create_application_key(
        self, name, open_command, description, new_file_entry, *, icon=None, run_as_admin_specification=None, default_command="open"
    ):
        if new_file_entry and description is None:
            raise ValueError("Description is required when creating a new file entry")

        # Create entry describing how to open a file with this application
        set_registry_value_string(HKCU, rf"SOFTWARE\Classes\{name}\shell\open\command", "", open_command, create_keys=True)

        # Select default shell command to execute on double-click
        set_registry_value_string(HKCU, rf"SOFTWARE\Classes\{name}\shell", "", default_command)

        # Provide textual description of the application or remove it completely
        if description:
            set_registry_value_string(HKCU, rf"SOFTWARE\Classes\{name}", None, description)
        else:
            delete_registry_value(HKCU, rf"SOFTWARE\Classes\{name}", None)
            delete_registry_value(HKLM, rf"SOFTWARE\Classes\{name}", None)

        # Provide icon for files with given extension
        if icon:
            set_registry_value_string(HKCU, rf"SOFTWARE\Classes\{name}\DefaultIcon", None, icon, create_keys=True)
        else:
            delete_registry_sub_key_tree(HKCU, rf"SOFTWARE\Classes\{name}", "DefaultIcon")
            delete_registry_sub_key_tree(HKLM, rf"SOFTWARE\Classes\{name}", "DefaultIcon")

        # Generate administrator command
        if run_as_admin_specification:
            runas_name, runas_command = run_as_admin_specification

            set_registry_value_string(HKCU, rf"SOFTWARE\Classes\{name}\shell\runas\Command", None, runas_command, create_keys=True)
            set_registry_value_string(HKCU, rf"SOFTWARE\Classes\{name}\shell\runas", None, runas_name)
        else:
            delete_registry_sub_key_tree(HKLM, rf"SOFTWARE\Classes\{name}", "runas")
            delete_registry_sub_key_tree(HKCU, rf"SOFTWARE\Classes\{name}", "runas")

    def _setup_extension(self, extension, application_key_name, new_file_entry):
        # Default value of the extension key points to application key. It can be empty, meaning
        # there is no application key associated.
        set_registry_value_string(HKCU, rf"SOFTWARE\Classes\{extension}", None, application_key_name, create_keys=True)

        # Clear previous settings
        self._clear_new_file_entry(extension)
        self._clear_user_choice(extension)

        # Setup entry in RMB->New context menu, if requested
        if new_file_entry:
            self._create_new_file_entry(extension)

    def _setup_extension_npp(self, npp_path, extension, description, new_file_entry):
        # Create application key for Notepad++ for this extension
        open_command = f'"{npp_path}" "%1"'
        application_key_name = f"PaiSetup{extension}"
        self._create_application_key(application_key_name, open_command, description, new_file_entry)

        # Associate extension with the application key
        self._setup_extension(extension, application_key_name, new_file_entry)

    def _setup_extension_powershell(self, extension, description, new_file_entry):
        app_path = run_command("where powershell", stdout=Stdout.return_back()).stdout.strip()
        open_command = f'"{app_path}" "%1"'
        application_key_name = f"PaiSetup{extension}"
        icon = f'"{app_path}",0'
        runas = ("Run with powershell (admin)", open_command)
        default_command = "Run with powershell"  # This command is already present in the system, we don't have to create it
        self._create_application_key(
            application_key_name,
            open_command,
            description,
            new_file_entry,
            icon=icon,
            run_as_admin_specification=runas,
            default_command=default_command,
        )

        self._setup_extension(extension, application_key_name, new_file_entry)


#    def extension_setup_imageglass:
#        param ($extension)
#
#        $helperKeyName = "ImageGlass.AssocFile$extension"
#
#        # Validate if there is an app key for this extension
#        $description = get_registry_default_value(HKCR, $helperKeyName
#        if (-Not $description):
#            echo "There is no ImageGlass helper key for $extension extension. Skipping"
#
#
#        extension_setup -extension $extension -helperKeyName $helperKeyName -newFileEntry $False
#
