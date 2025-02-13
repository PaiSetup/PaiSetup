import os

config_cache_path = os.environ["RPI_LED_CACHE"]
fifo_file_path = os.environ["RPI_LED_FIFO"]


class LedState:
    sections_count = 3
    sections_mask = (1 << sections_count) - 1

    def __init__(self):
        self.color = [0, 0, 100]
        self.enabled_sections = self.sections_mask
        self.brightness = 1

    def copy(self):
        new = LedState()
        new.color = self.color.copy()
        new.enabled_sections = self.enabled_sections
        new.brightness = self.brightness
        return new

    def to_message(self):
        color = self._adjust_brightness(self.color, self.brightness)
        tokens = color + [self.enabled_sections]
        tokens = [str(x) for x in tokens]
        return " ".join(tokens)

    @staticmethod
    def read_from_cache():
        state = LedState()
        try:
            with open(config_cache_path, "r") as file:
                line_count = 0
                for line in file:
                    line = line.strip()
                    if not state.apply_change(line):
                        print(f'WARNING: invalid command in cache file: "{line}"')
                    line_count += 1
            if line_count == 0:
                print("WARNING: empty cache file")
        except FileNotFoundError:
            pass
        return state

    def write_to_cache(self):
        tmp_config_cache_path = config_cache_path + ".tmp"

        commands = self.convert_to_commands()
        try:
            with open(tmp_config_cache_path, "w") as file:
                file.write(commands)
        except:
            return False

        os.rename(tmp_config_cache_path, config_cache_path)
        return True

    def write_to_fifo(self):
        commands = self.convert_to_commands()
        non_blocking_file_opener = lambda path, flags: os.open(path, flags | os.O_NONBLOCK)
        message = ""

        # First try writing to a FIFO file watched by rpi_led_client.py. If client is not
        # running, this will fail immediately.
        try:
            with open(fifo_file_path, "w", opener=non_blocking_file_opener) as file:
                file.write(commands)
            message = "Written to FIFO"
            success = True
        except OSError:
            # For FIFO files, If there's no reader, open(2) will return ENXIO. See fifo(7).
            message = "Could not connect to FIFO (no RPI client running)."
            success = False

        # If FIFO file was not connected, write to cache file instead as  a fallback, so
        # these settings will not be lost. The client will read them.
        if not success:
            success = self.write_to_cache()
            if success:
                message += " Written to cache."
            else:
                message += " Cache write failed."

        return (success, message)

    def apply_change(self, str):
        tokens = str.split(" ")
        try:
            match tokens[0]:
                case "c":
                    self.color = LedState._convert_tokens(tokens, int, 3, 0, 255)
                case "b":
                    self.brightness = LedState._convert_tokens(tokens, float, 1, 0.0, 1.0)[0]
                case "s":
                    self.enabled_sections = LedState._convert_tokens(tokens, int, 1, 0, LedState.sections_mask)[0]
                case _:
                    raise ValueError("Unknown command type")
            return True
        except ValueError as e:
            return False

    @staticmethod
    def _convert_tokens(tokens, data_type, count, min_value, max_value):
        if len(tokens) != 1 + count:
            raise ValueError("Invalid argument count")
        tokens_converted = [data_type(x) for x in tokens[1:]]
        if not all((min_value <= x <= max_value for x in tokens_converted)):
            raise ValueError("Invalid value range")
        return tokens_converted

    def convert_to_commands(self):
        values = {
            "c": " ".join((str(x) for x in self.color)),
            "b": self.brightness,
            "s": self.enabled_sections,
        }
        commands = [f"{cmd} {val}" for cmd, val in values.items()]
        commands = "\n".join(commands)
        commands += "\n"
        return commands

    def _adjust_brightness(self, rgb, brightness):
        def rgb_to_hsv(rgb):
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

        def hsv_to_rgb(hsv):
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

        hsv = rgb_to_hsv(rgb)
        hsv[2] = brightness
        rgb = hsv_to_rgb(hsv)
        rgb = [int(x * 100) for x in rgb]
        return rgb
