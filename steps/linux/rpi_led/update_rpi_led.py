#!/bin/python

import os
import select  # Linux-only

config_cache_path = os.environ["RPI_LED_CACHE"]
fifo_file_path = os.environ["RPI_LED_FIFO"]

timeout = 0.5


def non_blocking_file_opener(path, flags):
    return os.open(path, flags | os.O_NONBLOCK)


def main(color=None, brightness=None, enabled_sections=None, output_to_cache=False, silent=False, append=False):
    if output_to_cache:
        output_file = config_cache_path
        opener = None
    else:
        output_file = fifo_file_path
        opener = non_blocking_file_opener

    if type(color) == list:
        color = [str(x) for x in color]
        color = " ".join(color)

    values = {
        "c": color,
        "b": brightness,
        "s": enabled_sections,
    }
    commands = [f"{cmd} {val}" for cmd, val in values.items() if val is not None]
    commands = "\n".join(commands)
    commands += "\n"
    if not commands:
        return

    open_mode = "a" if append else "w"
    try:
        with open(output_file, mode=open_mode, opener=opener) as file:
            success = True
            message = f"Command: {commands}"
            file.write(commands)
    except OSError:
        success = False
        if not output_to_cache:
            # For FIFO files, If there's no reader, open(2) will return ENXIO. See fifo(7).
            message = "No RPI client running"
        else:
            raise

    if not silent:
        print(message)


if __name__ == "__main__":
    # fmt: off
    import argparse
    arg_parser = argparse.ArgumentParser(description="Update RPI LED config", allow_abbrev=False)
    arg_parser.add_argument("-c", "--color",      type=str,   default=None, help="RGB color to set in hex format.")
    arg_parser.add_argument("-b", "--brightness", type=float, default=None, help="Brightness to set (between 0 and 1).")
    arg_parser.add_argument("-s", "--sections",   type=int,   default=None, help="Integer mask of enabled sections.")
    args = arg_parser.parse_args()
    # fmt: on

    # Write to FIFO
    fifo_connected = main(args.color, args.brightness, args.sections, False, False, False)

    # If FIFO file was not connected, write to cache with append mode
    # so these settings will not be lost.
    if not fifo_connected:
        print("Writing to cache")
        main(args.color, args.brightness, args.sections, True, True, True)
