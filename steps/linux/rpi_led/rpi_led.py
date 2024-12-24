from pathlib import Path

from steps.step import Step


class RpiLedStep(Step):
    def __init__(self):
        super().__init__("RpiLed")
        self._daemon_path = Path(__file__).parent / "rpi_led_client.py"

    def express_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.add_packages("python-watchdog")

    def perform(self):
        self._file_writer.write_section(
            ".config/PaiSetup/xinitrc_base",
            "Run RPI led daemon",
            [f"{self._daemon_path} &"],
        )
