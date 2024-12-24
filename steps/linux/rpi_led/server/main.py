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

    def set_on_state(self, color, enabled_sections):
        self.enabled_sections = enabled_sections
        self.color = color
        self.mode = LedState.Mode_On
        self._write_timestamp += 1

    def set_invalid_state(self):
        self.mode = LedState.Mode_Invalid
        self._write_timestamp += 1

    def set_off_state(self):
        self.mode = LedState.Mode_Off
        self._write_timestamp += 1

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


async def handle_client(reader, writer):
    debug_log("Client connected")
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
            debug_log('Request "{line}" invalid - must be 4 tokens.')
            continue

        # Convert them ints.
        try:
            tokens_int = [int(x) for x in tokens]
        except ValueError:
            debug_log('Request "{line}" invalid - must be ints.')
            led_state.set_invalid_state()
            continue

        # Set valid state.
        color = tokens_int[0:3]
        enabled_sections = tokens_int[3]
        debug_log(f'Request "{line}" ok - color={color} enabled_sections={enabled_sections}')
        led_state.set_on_state(color, enabled_sections)

    debug_log("Client disconnected")
    led_state.set_off_state()


async def blink_debug_led(sleep_time, timeout=None):
    time_slept = 0
    while timeout is None or time_slept < timeout:
        await asyncio.sleep(sleep_time)
        time_slept += sleep_time
        debug_led.toggle()


async def control_led():
    # Constants
    animated_modes = [LedState.Mode_Uninitialized, LedState.Mode_Invalid]
    sleep_duration_normal = 0.1
    sleep_duration_animated = 0.02

    # Variables
    time_slept = 0

    # Main loop
    while True:
        is_animated_mode = led_state.mode in animated_modes

        # Async sleep to let other tasks work. Animated modes need shorted sleep time, so they
        # don't look snappy. Other modes can be updated more rarely, but it still can't be too
        # long, otherwise there will be a big delay.
        # TODO implement a more intelligent waiting mechanism. Maybe asyncio.Condition()?
        sleep_duration = sleep_duration_animated if is_animated_mode else sleep_duration_normal
        await asyncio.sleep(sleep_duration)
        time_slept += sleep_duration

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
asyncio.run(blink_debug_led(0.05, 1))
if not net.connect():
    print("Failed connecting to Wifi. Blinking sadly forever")
    asyncio.run(blink_debug_led(0.1))
print("Connected to Wifi")
net.set_hostname("RpiLed")

# Initialize state
led_state = LedState()
pin_number = 22
led.initialize(pin_number, led_state.get_led_count())

# Main tasks
loop = asyncio.get_event_loop()
loop.create_task(net.start_async_server(handle_client))
loop.create_task(blink_debug_led(1))
loop.create_task(control_led())
loop.run_forever()
