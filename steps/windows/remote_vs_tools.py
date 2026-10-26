from steps.step import Step
from utils.services.paths import KnownPath


class RemoteVsToolsStep(Step):
    def __init__(self):
        super().__init__("RemoteVsTools")

    def push_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_packages("visualstudio2022-remotetools")
        dependency_dispatcher.add_startup_entry("remote_debugger", self._get_bat_path(), as_admin=False)

    def perform(self):
        bat_path = self._get_bat_path()
        self._logger.log(f"Creating {bat_path}")
        bat_path.write_text(
            'start "" "C:\\Program Files\\Microsoft Visual Studio 17.0\\Common7\\IDE\\Remote Debugger\\x64\\msvsmon.exe"'
            " /noauth /anyuser /nosecuritywarn /nowowwarn /port 4020 /timeout:2147483646\n"
        )

    def _get_bat_path(self):
        return self._paths.get(KnownPath.Desktop) / "start_debugger.bat"
