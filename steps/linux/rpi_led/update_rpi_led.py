#!/bin/python

import os

config_cache_path = os.environ["RPI_LED_CACHE"]
fifo_file_path = os.environ["RPI_LED_FIFO"]


def main(color=None, brightness=None, enabled_sections=None, output_file=fifo_file_path):
    values = {
        "c": color,
        "b": brightness,
        "s": enabled_sections,
    }

    commands = [f"{cmd} {val}" for cmd, val in values.items() if val is not None]
    commands = "\n".join(commands)
    if commands:
        with open(output_file, "w") as file:
            file.write(commands)


if __name__ == "__main__":
    # fmt: off
    import argparse
    arg_parser = argparse.ArgumentParser(description="Update RPI LED config", allow_abbrev=False)
    arg_parser.add_argument("-c", "--color",      type=str,   default=None, help="RGB color to set in hex format.")
    arg_parser.add_argument("-b", "--brightness", type=float, default=None, help="Brightness to set (between 0 and 1).")
    arg_parser.add_argument("-s", "--sections",   type=int,   default=None, help="Integer mask of enabled sections.")
    arg_parser.add_argument("--cache",            action="store_true",      help="Store commands to the cache file. Otherwise, store to fifo file.")
    args = arg_parser.parse_args()
    # fmt: on

    output_file = config_cache_path if args.cache else fifo_file_path
    main(args.color, args.brightness, args.sections, output_file)
