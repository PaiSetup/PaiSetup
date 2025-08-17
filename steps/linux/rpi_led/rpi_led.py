from pathlib import Path

from steps.linux.spieven.spieven import SpievenDisplayType
from steps.step import Step
from utils.services.file_writer import LinePlacement


class RpiLedStep(Step):
    def __init__(self):
        super().__init__("RpiLed")
        self._daemon_path = Path(__file__).parent / "client/rpi_led_client.py"
        self._cache_file_path = self._env.home() / ".cache/PaiSetup/rpi_led_config"
        self._fifo_file_path = self._env.home() / ".config/PaiSetup/rpi_led_fifo"

    def push_dependencies(self, dependency_dispatcher):
        dependency_dispatcher.schedule_spieven_daemon("rpiled", self._daemon_path, display_type=SpievenDisplayType.Headless)

    def perform(self):
        # This must be done with LinePlacement.Begin, because env variables may
        # be used in select_wallpaper.py. The daemon could be started any time
        # and it would work.
        # TODO what if there are multiple displays? It will destroy the fifo file...
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
            ],
            line_placement=LinePlacement.Begin,
        )
