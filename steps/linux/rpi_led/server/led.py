import array
import time

import machine
import rp2


# Assembly program to drive the LED strip.
@rp2.asm_pio(sideset_init=rp2.PIO.OUT_LOW, out_shiftdir=rp2.PIO.SHIFT_LEFT, autopull=True, pull_thresh=24)
def ws2812():
    T1 = 2
    T2 = 5
    T3 = 3
    wrap_target()
    label("bitloop")
    out(x, 1).side(0)[T3 - 1]
    jmp(not_x, "do_zero").side(1)[T1 - 1]
    jmp("bitloop").side(1)[T2 - 1]
    label("do_zero")
    nop().side(0)[T2 - 1]
    wrap()


# Persistent data for this module.
led_state_machine = None
led_array = None


def initialize(pin_number, led_count):
    # Create the StateMachine with the ws2812 program, outputting on pin. It will wait
    # for data on its FIFO.
    global led_array
    led_array = array.array("I", [0 for _ in range(led_count)])

    # Prepare an array to store all values for LEDs.
    global led_state_machine
    led_state_machine = rp2.StateMachine(0, ws2812, freq=8_000_000, sideset_base=machine.Pin(pin_number))
    led_state_machine.active(1)


class LedContext:
    def __init__(self, initial_disable=True):
        if initial_disable:
            self.disable_all()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        led_state_machine.put(led_array, 8)
        time.sleep_ms(10)

    def disable_all(self):
        for i in range(len(led_array)):
            led_array[i] = 0

    def set(self, i, color):
        led_array[i] = (color[1] << 16) + (color[0] << 8) + color[2]
