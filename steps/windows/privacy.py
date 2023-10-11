from steps.step import Step
from utils import command
from utils.windows.windows_registry import *


class PrivacyStep(Step):
    def __init__(self):
        super().__init__("Privacy")

    def perform(self):
        self._logger.log("Disable Windows Feedback Experience program")
        set_registry_value_dword(HKLM, "SOFTWARE\Microsoft\Windows\CurrentVersion\AdvertisingInfo", "Enabled", "0", create_keys=True)
        set_registry_value_dword(HKCU, "SOFTWARE\Microsoft\Siuf\Rules", "PeriodInNanoSeconds", "0", create_keys=True)
        set_registry_value_dword(HKCU, "SOFTWARE\Microsoft\Siuf\Rules", "NumberOfSIUFInPeriod", "0")

        self._logger.log("Disable Cortana search")
        set_registry_value_dword(HKLM, "SOFTWARE\Microsoft\Windows\Windows Search", "AllowCortana", "0")

        self._logger.log("Disable Bing search")
        set_registry_value_dword(HKLM, "SOFTWARE\Policies\Microsoft\Windows\Windows Search", "DisableWebSearch", "1", create_keys=True)
        set_registry_value_dword(HKCU, "SOFTWARE\Microsoft\Windows\CurrentVersion\Search", "BingSearchEnabled", "0")

        self._logger.log("Disable cloud content")
        set_registry_value_dword(HKLM, "SOFTWARE\Policies\Microsoft\Windows\CloudContent", "DisableCloudOptimizedContent", "1", create_keys=True)
        set_registry_value_dword(HKLM, "SOFTWARE\Policies\Microsoft\Windows\CloudContent", "DisableSoftLanding", "1")
        set_registry_value_dword(HKLM, "SOFTWARE\Policies\Microsoft\Windows\CloudContent", "DisableWindowsConsumerFeatures", "1")
        set_registry_value_dword(HKCU, "SOFTWARE\Microsoft\Windows\CurrentVersion\ContentDeliveryManager", "ContentDeliveryAllowed", "0")
        set_registry_value_dword(HKCU, "SOFTWARE\Microsoft\Windows\CurrentVersion\ContentDeliveryManager", "OemPreInstalledAppsEnabled", "0")
        set_registry_value_dword(HKCU, "SOFTWARE\Microsoft\Windows\CurrentVersion\ContentDeliveryManager", "PreInstalledAppsEnabled", "0")
        set_registry_value_dword(HKCU, "SOFTWARE\Microsoft\Windows\CurrentVersion\ContentDeliveryManager", "PreInstalledAppsEverEnabled", "0")
        set_registry_value_dword(HKCU, "SOFTWARE\Microsoft\Windows\CurrentVersion\ContentDeliveryManager", "SilentInstalledAppsEnabled", "0")
        set_registry_value_dword(HKCU, "SOFTWARE\Microsoft\Windows\CurrentVersion\ContentDeliveryManager", "SystemPaneSuggestionsEnabled", "0")

        self._logger.log("Disable WiFi sense")
        set_registry_value_dword(HKLM, "SOFTWARE\Microsoft\PolicyManager\default\WiFi\AllowWiFiHotSpotReporting", "value", "0", create_keys=True)
        set_registry_value_dword(HKLM, "SOFTWARE\Microsoft\PolicyManager\default\WiFi\AllowAutoConnectToWiFiSenseHotspots", "value", "0")
        set_registry_value_dword(HKLM, "SOFTWARE\Microsoft\WcmSvc\wifinetworkmanager\config", "value", "0")

        self._logger.log("Disable telemetry")
        set_registry_value_dword(HKLM, "SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\DataCollection", "AllowTelemetry", "0")
        set_registry_value_dword(HKLM, "SOFTWARE\Policies\Microsoft\Windows\DataCollection", "AllowTelemetry", "0")
        set_registry_value_dword(HKLM, "SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\Policies\DataCollection", "AllowTelemetry", "0")

        self._logger.log("Disable location tracking")
        set_registry_value_dword(
            HKLM, "SOFTWARE\Microsoft\Windows NT\CurrentVersion\Sensor\Overrides\{BFA794E4-F964-4FDB-90F6-51056BFE4B44}", "SensorPermissionState", "0"
        )
        set_registry_value_dword(HKLM, "SYSTEM\CurrentControlSet\Services\lfsvc\Service\Configuration", "Status", "0", create_keys=True)

        self._logger.log("Disable typing information")
        set_registry_value_dword(HKCU, "SOFTWARE\Microsoft\Input\TIPC", "Enabled", "0")

        self._logger.log("Disable input personalization")
        set_registry_value_dword(HKCU, "SOFTWARE\Microsoft\Personalization\Settings", "AcceptedPrivacyPolicy", "0")
        set_registry_value_dword(HKCU, "SOFTWARE\Microsoft\Windows\CurrentVersion\SettingSync\Groups\Language", "Enabled", "0")
        set_registry_value_dword(HKCU, "SOFTWARE\Microsoft\InputPersonalization", "RestrictImplicitTextCollection", "1")
        set_registry_value_dword(HKCU, "SOFTWARE\Microsoft\InputPersonalization", "RestrictImplicitInkCollection", "1")
        set_registry_value_dword(HKCU, "SOFTWARE\Microsoft\InputPersonalization\TrainedDataStore", "HarvestContacts", "0")
