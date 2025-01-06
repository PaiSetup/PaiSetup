import math
import time

import debug_led
import led
import net
import uasyncio as asyncio


def debug_log(*args, **kwargs):
    print("DEBUG: ", end="")
    print(*args, **kwargs)


class LedState:
    Mode_Uninitialized = 0  # Default state
    Mode_On = 1  # State enabled when client periodically sends notifications
    Mode_Off = 2  # State enabled when client gets disconnected.
    Mode_Invalid = 3  # State enabled when client sends an invalid message

    def __init__(self):
        # Constants
        self._sections = [
            0,  # Left speaker
            8,  # Monitor
            28,  # Right speaker
            36,  # End
        ]

        # Led state
        self.mode = LedState.Mode_Uninitialized
        self.color = [0, 0, 0]
        self.enabled_sections = (1 << (len(self._sections) - 1)) - 1  # Bitfield of section indices

        # Timestamp state. Write timestamp is incremented when state changes. Read timestamp
        # is used to check if the state change was processed. Initialize them to different
        # values, so the initial state is processed.
        self._write_timestamp = 1
        self._read_timestamp = 0

        # Event variable to signal from TCP task to LED task, that state has been updated. Set the
        # event, so the initial state is processed.
        self._state_change_event = asyncio.Event()
        self._state_change_event.set()

    def _set_state(self, mode):
        self.mode = mode
        self._write_timestamp += 1
        self._state_change_event.set()

    def set_on_state(self, color, enabled_sections):
        self.enabled_sections = enabled_sections
        self.color = color
        self._set_state(LedState.Mode_On)

    def set_invalid_state(self):
        self._set_state(LedState.Mode_Invalid)

    def set_off_state(self):
        self._set_state(LedState.Mode_Off)

    def fetch_is_state_dirty(self):
        if self._write_timestamp != self._read_timestamp:
            self._read_timestamp = self._write_timestamp
            return True

        return False

    def get_enabled_leds(self):
        for section_index in range(len(self._sections) - 1):
            section_mask = 1 << section_index
            if (section_mask & self.enabled_sections) != 0:
                section_start = self._sections[section_index]
                section_end = self._sections[section_index + 1]
                for led_index in range(section_start, section_end):
                    yield led_index

    def get_all_leds(self):
        for led_index in range(self._sections[-1]):
            yield led_index

    def get_led_count(self):
        return self._sections[-1]

    async def wait_for_state_change(self, timeout):
        # await self._state_change_event.wait()
        try:
            await asyncio.wait_for(self._state_change_event.wait(), timeout)
            self._state_change_event.clear()
        except asyncio.TimeoutError:
            pass


async def handle_client(reader, writer):
    debug_log("Client connected")
    blink_config.off_time = 0.1

    while True:
        # Read line from the client and decode it as an ascii string. This could
        # be more efficient if it worked on bytes instead, but I guess it's fine.
        # It's not super perf-critical and it's a bit easier to test this way.
        line = await reader.readline()
        if not line:
            break
        line = line.decode().strip()

        # Break the input string into 4 tokens: three color components and one
        # enabled_sections bitfield.
        tokens = line.split(" ")
        if len(tokens) != 4:
            led_state.set_invalid_state()
            debug_log(f'Request "{line}" invalid - must be 4 tokens.')
            continue

        # Convert them ints.
        try:
            tokens_int = [int(x) for x in tokens]
        except ValueError:
            debug_log(f'Request "{line}" invalid - must be ints.')
            led_state.set_invalid_state()
            continue

        # Set valid state.
        color = tokens_int[0:3]
        enabled_sections = tokens_int[3]
        debug_log(f'Request "{line}" ok - color={color} enabled_sections={enabled_sections}')
        led_state.set_on_state(color, enabled_sections)

    debug_log("Client disconnected")
    blink_config.off_time = 1
    led_state.set_off_state()


class BlinkConfig:
    def __init__(self, on_time, off_time, timeout=None):
        self.on_time = on_time
        self.off_time = off_time
        self.timeout = timeout


async def blink_debug_led(blink_config):
    debug_led.off()
    is_on = False

    time_slept = 0
    while blink_config.timeout is None or time_slept < blink_config.timeout:
        if is_on:
            debug_led.off()
            is_on = False
            sleep_time = blink_config.on_time

        else:
            debug_led.on()
            is_on = True
            sleep_time = blink_config.off_time

        await asyncio.sleep(sleep_time)
        time_slept += sleep_time


async def control_led():
    # Constants
    animated_modes = [LedState.Mode_Uninitialized, LedState.Mode_Invalid]
    timeout_animated = 0.02

    # Variables
    time_slept = 0

    # Main loop
    while True:
        is_animated_mode = led_state.mode in animated_modes

        # Async wait to let other tasks work. Animated modes need a short timeout duration, so they
        # don't are regularly updated even though there's no mode change. Non-animated modes can
        # just wait indefinitely until something changes.
        timeout = timeout_animated if is_animated_mode else None
        await led_state.wait_for_state_change(timeout)

        # asyncio.sleep(sleep_duration)
        time_slept += timeout_animated

        # We don't have to always update the LED state. Skip the loop if nothing changed with an
        # exception for modes that we want to animate. Then always go into to LED control logic.
        if not led_state.fetch_is_state_dirty() and not is_animated_mode:
            continue

        # Set led state
        with led.LedContext() as led_context:
            if led_state.mode == LedState.Mode_On:
                # Set all LEDs to the same color
                for led_index in led_state.get_enabled_leds():
                    led_context.set(led_index, led_state.color)
            elif led_state.mode in animated_modes:
                # Set all LEDs to the pulsating light. Color is predefined based on the state.
                brightness = (math.sin(time_slept * 5) + 1) / 25
                color = {
                    LedState.Mode_Uninitialized: [brightness, brightness, brightness],
                    LedState.Mode_Invalid: [brightness, 0, 0],
                }
                color = color[led_state.mode]
                color = [int(255 * x) for x in color]
                for led_index in led_state.get_all_leds():
                    led_context.set(led_index, color)


# Connect to wifi
print("Connecting to Wifi")
asyncio.run(blink_debug_led(BlinkConfig(0.05, 0.05, 1)))
if not net.connect():
    print("Failed connecting to Wifi. Blinking sadly forever")
    asyncio.run(blink_debug_led(BlinkConfig(0.1, 0.1)))
print("Connected to Wifi")
net.set_hostname("RpiLed")

# Initialize state
led_state = LedState()
pin_number = 22
led.initialize(pin_number, led_state.get_led_count())

# Prepare global variable for blink config, so we can change it from other tasks.
blink_config = BlinkConfig(1, 1)

# Main tasks
loop = asyncio.get_event_loop()
loop.create_task(net.start_async_server(handle_client))
loop.create_task(blink_debug_led(blink_config))
loop.create_task(control_led())
loop.run_forever()
