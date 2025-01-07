#!/bin/python

from steps.linux.rpi_led.client.led_state import LedState


def main(query_color, query_brightness, query_enabled_sections):
    led_state = LedState.read_from_cache()

    # Gather queried results
    queried_results = []
    if query_color:
        queried_results.append(" ".join([str(x) for x in led_state.color]))
    if query_brightness:
        queried_results.append(led_state.brightness)
    if query_enabled_sections:
        queried_results.append(led_state.enabled_sections)

    # Print queried results
    for r in queried_results:
        print(r)


if __name__ == "__main__":
    # fmt: off
    import argparse
    arg_parser = argparse.ArgumentParser(description="Query RPI LED config. Regardless of command-line arguments order, fields will always be reported in order color, brightness, enabled_sections.", allow_abbrev=False)
    arg_parser.add_argument("-c", "--color",      action="store_true", help="Query color.")
    arg_parser.add_argument("-b", "--brightness", action="store_true", help="Query brightness.")
    arg_parser.add_argument("-s", "--sections",   action="store_true", help="Query enabled sections.")
    args = arg_parser.parse_args()
    # fmt: on

    main(args.color, args.brightness, args.sections)
