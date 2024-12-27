from pathlib import Path

from steps.step import Step


class RpiLedStep(Step):
    def __init__(self):
        super().__init__("RpiLed")
        self._daemon_path = Path(__file__).parent / "rpi_led_client.py"
        self._cache_file_path = self._env.home() / ".cache/PaiSetup/rpi_led_config"
        self._fifo_file_path = self._env.home() / ".config/PaiSetup/rpi_led_fifo"

    def perform(self):
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
                f"{self._daemon_path} &",
            ],
        )
