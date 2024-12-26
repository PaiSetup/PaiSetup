#!/bin/python

import os
import os.path
import sys

home_path = os.environ["HOME"]
config_path = f"{home_path}/.config/PaiSetup/rpi_led_config"


class BrightnessAdjuster:
    @staticmethod
    def adjust_brightness(rgb, brightness):
        hsv = BrightnessAdjuster._rgb_to_hsv(rgb)
        hsv[2] = brightness
        rgb = BrightnessAdjuster._hsv_to_rgb(hsv)
        rgb = [int(x * 100) for x in rgb]
        return rgb

    @staticmethod
    def _rgb_to_hsv(rgb):
        r = rgb[0]
        g = rgb[1]
        b = rgb[2]
        maxc = max(r, g, b)
        minc = min(r, g, b)
        v = maxc
        if minc == maxc:
            return [0.0, 0.0, v]
        s = (maxc - minc) / maxc
        rc = (maxc - r) / (maxc - minc)
        gc = (maxc - g) / (maxc - minc)
        bc = (maxc - b) / (maxc - minc)
        if r == maxc:
            h = bc - gc
        elif g == maxc:
            h = 2.0 + rc - bc
        else:
            h = 4.0 + gc - rc
        h = (h / 6.0) % 1.0
        return [h, s, v]

    @staticmethod
    def _hsv_to_rgb(hsv):
        h = hsv[0]
        s = hsv[1]
        v = hsv[2]
        if s == 0.0:
            return v, v, v
        i = int(h * 6.0)
        f = (h * 6.0) - i
        p = v * (1.0 - s)
        q = v * (1.0 - s * f)
        t = v * (1.0 - s * (1.0 - f))
        i = i % 6
        if i == 0:
            return [v, t, p]
        if i == 1:
            return [q, v, p]
        if i == 2:
            return [p, v, t]
        if i == 3:
            return [p, q, v]
        if i == 4:
            return [t, p, v]
        if i == 5:
            return [v, p, q]


class LedState:
    sections_count = 3
    sections_mask = (1 << sections_count) - 1

    def __init__(self):
        self.color = [0, 0, 100]
        self.enabled_sections = self.sections_mask
        self.brightness = 1

    def apply(self, logger, color, brightness, enabled_sections):
        # Validate
        if color is not None:
            if type(color) == list and len(color) == 3:
                pass
            elif type(color) == str and len(color) == 6:
                color = LedState.hex_color_to_list(color)
                if color is None:
                    logger.push_warning("Invalid color passed")
                    return False
            else:
                logger.push_warning("Invalid color passed")
                return False
        if brightness is not None:
            if type(brightness) != float:
                logger.push_warning("Invalid brightness passed")
                return False
        if enabled_sections is not None:
            if type(enabled_sections) != int:
                logger.push_warning("Invalid enabled_sections passed")
                return False

        # Set
        if color is not None:
            self.color = color
        if brightness is not None:
            self.brightness = brightness
        if enabled_sections is not None:
            self.enabled_sections = enabled_sections

        # Apply brightness
        print(self.color)
        self.color = BrightnessAdjuster.adjust_brightness(self.color, self.brightness)
        print(self.color)

        return True

    @staticmethod
    def hex_color_to_list(string):
        if len(string) != 6:
            return None

        color = [
            string[0:2],
            string[2:4],
            string[4:6],
        ]
        color = [int(x, 16) for x in color]
        return color

    @staticmethod
    def from_string(string):
        tokens = string.strip().split(" ")
        if len(tokens) != 4:
            print("")
            return LedState()

        try:
            tokens = [int(x) for x in tokens]
        except ValueError:
            return LedState()

        color = tokens[0:3]
        enabled_sections = tokens[3]

        if enabled_sections > LedState.sections_mask:
            return LedState()

        result = LedState()
        result.color = color
        result.enabled_sections = enabled_sections
        return result

    def __str__(self):
        tokens = self.color + [self.enabled_sections]
        tokens = [str(x) for x in tokens]
        return " ".join(tokens) + "\n"


class BackupLogger:
    def push_warning(self, message):
        print(f"WARNING: {message}")

    def log(self, message):
        print(message)


def main(logger=None, color=None, brightness=None, enabled_sections=None):
    if logger is None:
        logger = BackupLogger()

    is_modify_file = os.path.isfile(config_path)
    openmode = "r+" if is_modify_file else "w"

    file = open(config_path, openmode)

    if is_modify_file:
        state = file.read()
        state = LedState.from_string(state)
        file.seek(0)
    else:
        state = LedState()

    apply_success = state.apply(logger, color, brightness, enabled_sections)
    if not apply_success:
        return False

    file.write(str(state))
    if is_modify_file:
        file.truncate()

    file.close()
    return True


if __name__ == "__main__":
    # fmt: off
    import argparse
    arg_parser = argparse.ArgumentParser(description="Update RPI LED config", allow_abbrev=False)
    arg_parser.add_argument("-c", "--color",      type=str,   default=None, help="RGB color to set in hex format.")
    arg_parser.add_argument("-b", "--brightness", type=float, default=None, help="Brightness to set (between 0 and 1).")
    arg_parser.add_argument("-s", "--sections",   type=int,   default=None, help="Integer mask of enabled sections.") # Add range
    args = arg_parser.parse_args()
    # fmt: on

    success = main(BackupLogger(), args.color, args.brightness, args.sections)
    sys.exit(0 if success else 1)
