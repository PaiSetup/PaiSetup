from pathlib import Path

from steps.step import Step
from utils.services.file_writer import LinePlacement


class RpiLedStep(Step):
    def __init__(self):
        super().__init__("RpiLed")
        self._daemon_path = Path(__file__).parent / "client/rpi_led_client.py"
        self._cache_file_path = self._env.home() / ".cache/PaiSetup/rpi_led_config"
        self._fifo_file_path = self._env.home() / ".config/PaiSetup/rpi_led_fifo"

    def express_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.register_periodic_daemon_check("[a-zA-Z/]+python[23]? [a-zA-Z_/]+/rpi_led/client/rpi_led_client.py", "rpi_led_client")

    def perform(self):
        # This must be done with LinePlacement.Begin, because env variables may
        # be used in select_wallpaper.py. The daemon could be started any time
        # and it would work.
        self._file_writer.write_section(
            ".config/PaiSetup/xinitrc_base",
            "Setup and run rpi_Led daemon",
            [
                f'export RPI_LED_CACHE="{self._cache_file_path}"',
                f'export RPI_LED_FIFO="{self._fifo_file_path}"',
                f'if ! [ -p "$RPI_LED_FIFO" ]; then',
                f'    rm -f "$RPI_LED_FIFO"',
                f'    mkfifo "$RPI_LED_FIFO"',
                f"fi",
                f"pkill -f '{self._daemon_path.name}'",
                f"{self._daemon_path} &",
            ],
            line_placement=LinePlacement.Begin,
        )
