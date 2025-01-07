#!/bin/python

from steps.linux.rpi_led.client.led_state import LedState


def main(color=None, brightness=None, enabled_sections=None, silent=False):
    # Read current state from cache file. If there's no cache file, we'll get a defaulted state
    led_state = LedState.read_from_cache()

    # Apply all changes passed from command line
    changes = {
        "c": color,
        "b": brightness,
        "s": enabled_sections,
    }
    changes = [f"{k} {v}" for k, v in changes.items() if v is not None]
    success = all((led_state.apply_change(c) for c in changes))
    if not success:
        print("Could not apply all parameters")
        return

    # Write changed led state to fifo file with a fallback to cache file
    success, message = led_state.write_to_fifo()
    if not silent:
        print(f"Commands:\n{led_state.convert_to_commands()}")
        print(message)

    return success


if __name__ == "__main__":
    # fmt: off
    import argparse
    arg_parser = argparse.ArgumentParser(description="Update RPI LED config", allow_abbrev=False)
    arg_parser.add_argument("-c", "--color",      type=str,   default=None, help="RGB color to set in hex format.")
    arg_parser.add_argument("-b", "--brightness", type=float, default=None, help="Brightness to set (between 0 and 1).")
    arg_parser.add_argument("-s", "--sections",   type=int,   default=None, help="Integer mask of enabled sections.")
    args = arg_parser.parse_args()
    # fmt: on

    main(args.color, args.brightness, args.sections)
