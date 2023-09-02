from steps.step import Step
from utils import command


class UninstallBloatStep(Step):
    def __init__(self):
        super().__init__("UninstallBloat")

    def perform(self):
        unnecessary_microsoft_apps = [
            "*Microsoft.ScreenSketch*",
            "*Microsoft.Office.OneNote*",
            "*Microsoft.Todos*",
            "*Microsoft.StorePurchaseApp*",
            "*Microsoft.MSPaint*",
            "*Microsoft.BingNews*",
            "*Microsoft.BingWeather*",
            "*Microsoft.GetHelp*",
            "*Microsoft.Getstarted*",
            "*Microsoft.Messaging*",
            "*Microsoft.Microsoft3DViewer*",
            "*Microsoft.MicrosoftOfficeHub*",
            "*Microsoft.MicrosoftSolitaireCollection*",
            "*Microsoft.MixedReality.Portal*",
            "*Microsoft.NetworkSpeedTest*",
            "*Microsoft.Office.Sway*",
            "*Microsoft.OneConnect*",
            "*Microsoft.People*",
            "*Microsoft.Print3D*",
            "*Microsoft.SkypeApp*",
            "*Microsoft.Wallet*",
            "*Microsoft.WindowsAlarms*",
            "*Microsoft.WindowsCamera*",
            "*Microsoft.WindowsFeedbackHub*",
            "*Microsoft.WindowsMaps*",
            "*Microsoft.WindowsSoundRecorder*",
            "*Microsoft.Xbox.TCUI*",
            "*Microsoft.XboxApp*",
            "*Microsoft.XboxGameOverlay*",
            "*Microsoft.XboxGamingOverlay*",
            "*Microsoft.XboxIdentityProvider*",
            "*Microsoft.XboxSpeechToTextOverlay*",
            "*Microsoft.YourPhone*",
            "*Microsoft.ZuneMusic*",
            "*Microsoft.ZuneVideo*",
            "*microsoft.windowscommunicationsapps*",
        ]

        sponsored_apps = [
            "*EclipseManager*",
            "*ActiproSoftwareLLC*",
            "*AdobeSystemsIncorporated.AdobePhotoshopExpress*",
            "*Duolingo-LearnLanguagesforFree*",
            "*PandoraMediaInc*",
            "*CandyCrush*",
            "*Wunderlist*",
            "*Flipboard*",
            "*Twitter*",
            "*Facebook*",
            "*Spotify*",
            "*king.com.BubbleWitch3Saga*",
        ]

        powershell_script = [
            "function uninstall_app { param($appName)",
            "",
            "    $output = Get-AppxPackage -Name $appName -AllUsers",
            "    if ($output) {",
            '        echo "Removing appx package: $appName"',
            "        $output | Remove-AppxPackage -ErrorAction SilentlyContinue",
            "        return",
            "    }",
            "",
            "}",
        ]

        """
        Microsoft Store apps can also be installed as "appx provisioned packages". I am not sure if we should also search
        these apps, but it should work with this code. It takes quite a lot of time though, so keeping it commented for
        now. If it's needed, maybe execute it only for apps, that we now can be provisioned to save time.

            "    $output = Get-AppxProvisionedPackage -Online | Where-Object DisplayName -like $appName",
            "    if ($output) {",
            '        echo "$appName is installed as provisioned package"',
            "        $output | Remove-AppxProvisionedPackage -Online -ErrorAction SilentlyContinue | out-null",
            "        return",
            "    }",
        """

        for app in unnecessary_microsoft_apps + sponsored_apps:
            powershell_script.append(f"uninstall_app {app}")
        command.run_powershell_command(powershell_script, print_stdout=True)
