from steps.step import Step


class RemoteVsToolsStep(Step):
    def __init__(self):
        super().__init__("RemoteVsTools")
        self._bat_path = self._env.home() / "Desktop" / "start_debugger.bat"

    def push_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_packages("visualstudio2022-remotetools")
        dependency_dispatcher.add_startup_entry("remote_debugger", self._bat_path, as_admin=False)

    def perform(self):
        self._logger.log(f"Creating {self._bat_path}")
        self._bat_path.write_text(
            'start "" "C:\\Program Files\\Microsoft Visual Studio 17.0\\Common7\\IDE\\Remote Debugger\\x64\\msvsmon.exe"'
            " /noauth /anyuser /nosecuritywarn /nowowwarn /port 4020 /timeout:2147483646\n"
        )
